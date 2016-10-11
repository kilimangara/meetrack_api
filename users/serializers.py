from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'created', 'hidden_phone', 'avatar']
        read_only_fields = ['created', 'phone']


class UserIdsSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())

    def registered_users(self):
        ids = set(self.validated_data['user_ids'])
        return User.objects.filter(id__in=ids).distinct('id')

    def registered_user_ids(self):
        ids = set(self.validated_data['user_ids'])
        return User.objects.filter(id__in=ids).values_list('id', flat=True).distinct('id')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'created', 'avatar']

    def to_representation(self, instance):
        viewer = self.context['viewer']
        contact = viewer.contacts.filter(to=instance.id).first()
        if contact:
            instance.name = contact.name
            data = super().to_representation(instance)
        elif viewer == instance:
            data = AccountSerializer(instance).data
        else:
            data = super().to_representation(instance)
            if instance.hidden_phone or viewer in instance.blacklist:
                del data['phone']

        return data
