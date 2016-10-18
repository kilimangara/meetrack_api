from rest_framework import serializers
from .models import Meeting, Member


class MeetingsListTypeSerializer(serializers.Serializer):
    all = serializers.BooleanField(default=False)


class MeetingSerializer(serializers.ModelSerializer):
    king = serializers.SerializerMethodField(read_only=True)
    users = serializers.SerializerMethodField(read_only=True)

    @classmethod
    def get_king(cls, obj):
        return obj.king.id

    @classmethod
    def get_users(cls, obj):
        return obj.users.values_list('id', flat=True)

    class Meta:
        model = Meeting
        fields = ['id', 'title', 'description', 'logo', 'time', 'created', 'completed', 'king', 'users']
        read_only_fields = ['created', 'completed']
        extra_kwargs = {
            'description': {
                'required': False,
            }
        }
