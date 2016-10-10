from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'created']
        read_only_fields = ['created', 'phone']


class UsersIdsSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())

    def registered_users(self):
        ids = set(self.validated_data['ids'])
        return User.objects.filter(id__in=ids).distinct('id')


class ForeignUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        pass

    def to_representation(self, instance):
        viewer = self.context['viewer']
        contact = viewer.contacts.filter(to=instance.id).first()
        if contact:
            instance.name = contact.name
            data = super().to_representation(instance)
        else:
            data = super().to_representation(instance)
            del data['phone']
        return data
