from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Meeting

User = get_user_model()


class MeetingsListTypeSerializer(serializers.Serializer):
    all = serializers.BooleanField(default=False)


class MeetingSerializer(serializers.ModelSerializer):
    king = serializers.SerializerMethodField(read_only=True)
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    @classmethod
    def get_king(cls, obj):
        return None

    def create(self, validated_data):
        king = self.context['king']
        users = validated_data['users']
        users.append(king)
        users = set(users)
        validated_data['users'] = users
        return super().create(validated_data)

    class Meta:
        model = Meeting
        fields = ['id', 'title', 'description', 'logo', 'time', 'created', 'completed', 'king', 'users']
        read_only_fields = ['created', 'completed']
        extra_kwargs = {
            'description': {
                'required': False,
            }
        }
