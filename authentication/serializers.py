import random
import string

import phonenumbers
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, Throttled

from . import token_storage
from .phone_storage import Phone, PhoneDoesNotExist

User = get_user_model()


class PhoneNumberField(serializers.CharField):
    default_error_messages = {
        'invalid': _('Invalid phone number.'),
    }

    def to_internal_value(self, data):
        try:
            phone = phonenumbers.parse(data)
        except NumberParseException:
            self.fail('invalid')
        if not phonenumbers.is_valid_number(phone):
            self.fail('invalid')
        return data


class SendingError(Exception):
    pass


class SendPhoneSerializer(serializers.Serializer):
    CODE_LENGTH = 5
    phone = PhoneNumberField()

    def generate_code(self):
        return ''.join(random.choice(string.digits) for _ in range(self.CODE_LENGTH))

    def send_code(self):
        phone = self.validated_data['phone']
        code = self.validated_data['code']
        r = requests.post(settings.SMS_AUTH['REQUEST_URL'],
                          data={'To': phone, 'From': settings.SMS_AUTH['FROM_NUMBER'], 'Body': code},
                          auth=(settings.SMS_AUTH['ACCOUNT_SID'], settings.SMS_AUTH['AUTH_TOKEN']))
        if r.status_code != 201:
            raise SendingError("Service response has incorrect status code", r)

    def validate(self, attrs):
        phone = Phone(attrs['phone'])
        count = phone.get_attempts()
        if count >= settings.SMS_AUTH['ATTEMPTS_LIMIT']:
            raise Throttled()
        return attrs

    def save_code(self, code=None):
        if code is None:
            code = self.generate_code()
        phone = Phone(self.validated_data['phone'])
        phone.create(code, time=settings.SMS_AUTH['LIFE_TIME'])
        self.validated_data['code'] = code
        return code


class ConfirmPhoneSerializer(SendPhoneSerializer):
    validation_error = ValidationError({'code': ['Code is invalid.']})
    code = serializers.CharField(max_length=SendPhoneSerializer.CODE_LENGTH, min_length=SendPhoneSerializer.CODE_LENGTH)
    is_new = serializers.BooleanField(default=False, write_only=True)

    def validate(self, attrs):
        phone_number = attrs['phone']
        code = attrs['code']
        if settings.DEBUG and code == settings.SMS_AUTH['DEBUG_CODE']:
            return attrs
        phone = Phone(phone_number)
        try:
            real_code, count = phone.get()
        except PhoneDoesNotExist:
            raise self.validation_error
        if count >= settings.SMS_AUTH['ATTEMPTS_LIMIT']:
            raise Throttled()
        if code != real_code:
            phone.set_attempts(attempts=count + 1)
            raise self.validation_error
        phone.delete()
        return attrs


class NewUserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        return self.validated_data['token_value']

    def create(self, validated_data):
        user = super().create(validated_data)
        self.validated_data['token_value'] = token_storage.create(user.id)
        return user

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'created', 'token', 'avatar']
        read_only_fields = ['created', 'token']
