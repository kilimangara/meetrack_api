import phonenumbers
from django.contrib.auth import get_user_model
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework import serializers

User = get_user_model()


class PhoneNumberField(serializers.CharField):
    default_error_messages = {
        'invalid': "The phone number has incorrect format."
    }

    def to_internal_value(self, data):
        try:
            phone = phonenumbers.parse(data)
        except NumberParseException:
            self.fail('invalid')
        if not phonenumbers.is_valid_number(phone):
            self.fail('invalid')
        return data


class ForeignUserIdSerializer(serializers.Serializer):
    user = serializers.IntegerField()

    def validate_user(self, value):
        viewer = self.context['viewer']
        if viewer.id == value:
            raise serializers.ValidationError("Can not do it with yourself.")
        return value
