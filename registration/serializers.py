import random
import string

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from users.models import User


class ErrorToTextMixin(object):
    @property
    def errors_as_text(self):
        assert isinstance(self, serializers.Serializer)
        errors_list = []
        for field, field_errors in self.errors.items():
            if not field_errors:
                continue
            errors_list.append('{}: {}'.format(field, field_errors[0]))
        text = ' '.join(errors_list)
        return text


class PhoneSerializer(serializers.Serializer, ErrorToTextMixin):
    phone = PhoneNumberField()


class CodeSerializer(serializers.Serializer, ErrorToTextMixin):
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
