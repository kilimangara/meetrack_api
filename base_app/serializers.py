import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework import serializers


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
