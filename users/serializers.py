from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'phone', 'created']
