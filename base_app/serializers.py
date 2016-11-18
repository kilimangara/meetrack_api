import phonenumbers
from django.contrib.auth import get_user_model
from phonenumbers.phonenumberutil import NumberParseException
from phonenumber_field import phonenumber
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers
from django.core.exceptions import ValidationError

User = get_user_model()


class PhoneNumberField(serializers.CharField):
    default_error_messages = {
        'invalid': "The phone number has incorrect format."
    }

    def to_internal_value(self, data):
        phone_number = phonenumber.to_python(data)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid'])
        return phone_number


class ForeignUserIdSerializer(serializers.Serializer):
    user = serializers.IntegerField()

    def validate_user(self, value):
        viewer = self.context['viewer']
        if viewer.id == value:
            raise serializers.ValidationError("Can not do it with yourself.")
        return value
