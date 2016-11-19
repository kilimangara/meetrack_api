from collections import OrderedDict

from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import FIELD_MAX_LENGTH

User = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'created_at', 'hidden_phone', 'avatar']
        read_only_fields = ['created_at', 'phone']


class UserIdsSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        viewer = self.context['viewer']
        contacts = {c.user_to_id: c for c in viewer.contacts.all()}
        self.context['contacts'] = contacts
        self.context['blocked_viewer'] = set(viewer.blocked_me.all())

    def to_representation(self, instance):
        viewer = self.context['viewer']
        contact = self.context['contacts'].get(instance.id)
        blocked_viewer = self.context['blocked_viewer']
        if contact:
            instance.name = contact.name
            data = super().to_representation(instance)
        elif viewer == instance:
            data = AccountSerializer(instance).data
        else:
            data = super().to_representation(instance)
            if instance.hidden_phone or instance in blocked_viewer:
                del data['phone']
        return data


class ImportContactsSerializer(serializers.Serializer):
    phones = serializers.ListField(child=PhoneNumberField(), allow_empty=False, write_only=True)
    names = serializers.ListField(child=serializers.CharField(max_length=FIELD_MAX_LENGTH), allow_empty=False,
                                  write_only=True)

    def validate_phones(self, value):
        phones = value
        phones_unique = OrderedDict.fromkeys(phones)
        user = self.context['user']
        if len(phones_unique) != len(phones):
            raise ValidationError("Phone list contains duplicates.")
        elif user.phone in phones:
            raise ValidationError("The phones list contains user phone.")
        return list(phones_unique)

    def validate(self, attrs):
        names = attrs['names']
        phones = attrs['phones']
        if len(names) != len(phones):
            raise ValidationError("The number of phones must be equal to the number of names.")
        return attrs


class DeleteContactsSerializer(serializers.Serializer):
    phones = serializers.ListField(child=PhoneNumberField(), allow_empty=False, write_only=True)
