import random
import string

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, Throttled
from base_app.serializers import PhoneNumberField

from .phone_storage import PhoneStorage, CodeDoesNotExist

User = get_user_model()


class SMSSendingError(Exception):
    pass


class PhoneSerializer(serializers.Serializer):
    phone = PhoneNumberField()


class CodeSerializer(serializers.Serializer):
    CODE_LENGTH = 5
    code = serializers.CharField(max_length=CODE_LENGTH, min_length=CODE_LENGTH)

    @classmethod
    def generate_code(cls):
        return ''.join(random.choice(string.digits) for _ in range(cls.CODE_LENGTH))


class IsNewUserSerializer(serializers.Serializer):
    is_new = serializers.BooleanField(default=False, write_only=True)


class ConfirmPhoneSerializer(PhoneSerializer):
    code_error = ValidationError({'code': ['Code is invalid.']})
    code = serializers.CharField(max_length=PhoneSerializer.CODE_LENGTH, min_length=PhoneSerializer.CODE_LENGTH)
    is_new = serializers.BooleanField(default=False, write_only=True)

    def validate(self, attrs):
        phone_number = attrs['phone']
        code = attrs['code']
        if settings.DEBUG and code == settings.SMS_AUTH['DEBUG_CODE']:
            return attrs
        phone = PhoneStorage(phone_number)
        try:
            real_code = phone.get_code()
        except CodeDoesNotExist:
            raise self.code_error
        count = phone.get_attempts()
        if count >= settings.SMS_AUTH['ATTEMPTS_LIMIT']:
            raise self.throttled_error
        if code != real_code:
            phone.increment_attempts(lifetime=settings.SMS_AUTH['ATTEMPTS_LIFE_TIME'])
            raise self.code_error
        return attrs

    def deactivate_code(self):
        phone_number = self.validated_data['phone']
        PhoneStorage(phone_number).delete_code()

    def reuse_code(self):
        code = self.validated_data['code']
        phone_number = self.validated_data['phone']
        PhoneStorage(phone_number).set_code(code)


class NewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone', 'avatar']
        extra_kwargs = {
            'avatar': {
                'required': False
            }
        }
