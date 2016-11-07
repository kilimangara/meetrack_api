import random
import string

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, Throttled
from common_fields.serializers import PhoneNumberField

from .phone_storage import PhoneStorage, PhoneDoesNotExist

User = get_user_model()


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
        phone = PhoneStorage(attrs['phone'])
        count = phone.get_attempts()
        if count >= settings.SMS_AUTH['ATTEMPTS_LIMIT']:
            raise Throttled()
        return attrs

    def save_code(self, code=None):
        if code is None:
            code = self.generate_code()
        phone = PhoneStorage(self.validated_data['phone'])
        phone.set_code(code, time=settings.SMS_AUTH['CODE_LIFE_TIME'])
        phone.increment_attempts(time=settings.SMS_AUTH['ATTEMPTS_LIFE_TIME'])
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
        phone = PhoneStorage(phone_number)
        try:
            real_code = phone.get_code()
        except PhoneDoesNotExist:
            raise self.validation_error
        count = phone.get_attempts()
        if count >= settings.SMS_AUTH['ATTEMPTS_LIMIT']:
            raise Throttled()
        if code != real_code:
            phone.increment_attempts(time=settings.SMS_AUTH['ATTEMPTS_LIFE_TIME'])
            raise self.validation_error
        phone.delete()
        return attrs


class NewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone', 'avatar']
