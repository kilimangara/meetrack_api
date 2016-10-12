from collections import OrderedDict

from bulk_update.helper import bulk_update
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.serializers import PhoneNumberField
from .models import FIELD_MAX_LENGTH, Contact

User = get_user_model()


class ImportContactSerializer(serializers.Serializer):
    phones = serializers.ListField(child=PhoneNumberField(), allow_empty=False, write_only=True)
    names = serializers.ListField(child=serializers.CharField(max_length=FIELD_MAX_LENGTH), allow_empty=False,
                                  write_only=True)

    @classmethod
    def validate_phones(cls, value):
        phones = value
        phones_unique = list(OrderedDict.fromkeys(phones))
        if len(phones_unique) != len(phones):
            raise ValidationError("Phone list contains duplicates.")
        return phones_unique

    def validate(self, attrs):
        names = attrs['names']
        phones = attrs['phones']
        user = self.context['user']
        if len(names) != len(phones):
            raise ValidationError("The number of phones must be equal to the number of names.")
        if user.phone in phones:
            raise ValidationError("The phones list contains user phone.")
        return attrs

    def create(self, validated_data):
        user = self.context['user']
        input_contacts = dict(zip(validated_data['phones'], validated_data['names']))
        old_contacts = user.contacts.filter(phone__in=input_contacts.keys())
        imported_contacts = []
        for contact in old_contacts:
            phone = contact.phone
            contact.active = True
            contact.name = input_contacts[phone]
            input_contacts.pop(phone)
            if contact.to_id is not None:
                imported_contacts.append(contact.to_id)
        registered_phones = dict(User.objects.filter(phone__in=input_contacts.keys()).values_list('phone', 'id'))
        to_create = []
        for phone, name in input_contacts.items():
            to_id = registered_phones.get(phone, None)
            c = Contact(owner=user, to_id=to_id, phone=phone, name=name)
            to_create.append(c)
            if to_id is not None:
                imported_contacts.append(c.to_id)
        with atomic():
            bulk_update(old_contacts, update_fields=['name', 'active'])
            Contact.objects.bulk_create(to_create)
        return User.objects.filter(id__in=imported_contacts)


class DeleteContactsSerializer(serializers.Serializer):
    phones = serializers.ListField(child=PhoneNumberField(), allow_empty=False, write_only=True)

    def create(self, validated_data):
        user = self.context['user']
        phones = validated_data['phones']
        contacts = user.contacts.filter(phone__in=phones)
        for c in contacts:
            c.active = False
        bulk_update(contacts, update_fields=['active'])
        return validated_data
