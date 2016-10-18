from rest_framework import serializers
from .models import Meeting, Member


class MeetingSerializer(serializers.ModelSerializer):
    king = serializers.SerializerMethodField()
    users=serializers.Serializer

    def get_king(self, obj):
        return obj.king().id

    class Meta:
        model = Meeting
        fields = ['title', 'description', 'logo', 'time', 'created', 'completed', 'king']
        read_only_fields = ['created', 'completed']
