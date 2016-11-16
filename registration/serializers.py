import random
import string

from django.contrib.auth import get_user_model
from rest_framework import serializers

from base_app.serializers import PhoneNumberField

User = get_user_model()


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


class NewUserSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = ['name', 'phone', 'avatar']
        extra_kwargs = {
            'avatar': {
                'required': False
            }
        }
