from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Meeting, Member

User = get_user_model()


class ForeignUserIdSerializer(serializers.Serializer):
    user = serializers.IntegerField()

    def validate_user(self, value):
        viewer = self.context['viewer']
        if viewer.id == value:
            raise ValidationError("Can not do it with yourself.")
        elif not User.objects.filter(id=value).exists():
            raise ValidationError("User with this id does not exist.")
        return value


class MeetingsListTypeSerializer(serializers.Serializer):
    completed = serializers.BooleanField(default=False)


class MembersSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.IntegerField())

    def to_internal_value(self, data):
        v = super().to_internal_value(data)
        user_ids = v['users']
        king = self.context['king']
        user_ids.append(king.id)
        blocked = king.inbound_blocks.values_list('user_from_id', flat=True)
        user_ids = User.objects.filter(
            id__in=user_ids).exclude(id__in=blocked).distinct('id').values_list('id', flat=True)
        v['users'] = user_ids
        return v


class MeetingSerializer(serializers.ModelSerializer):
    king = serializers.SerializerMethodField(read_only=True)

    def get_king(self, obj):
        return self.context.get('king_id') or obj.king_id

    def create(self, validated_data):
        m = super().create(validated_data)
        user_ids = self.context['user_ids']
        king_id = self.context['king_id']
        members = [Member(user_id=uid, meeting=m, king=uid == king_id) for uid in user_ids]
        Member.objects.bulk_create(members)
        return m

    class Meta:
        model = Meeting
        fields = ['id', 'title', 'description', 'logo', 'end_at', 'created_at', 'completed', 'king', 'users']
        read_only_fields = ['created_at', 'completed']
        extra_kwargs = {
            'description': {
                'required': False
            },
            'end_at': {
                'required': False
            }
        }


class MeetingUpdateSerializer(serializers.ModelSerializer):
    @classmethod
    def validate_completed(cls, value):
        completed = value
        if not completed:
            raise ValidationError("completed must be True or not specified.")
        return completed

    class Meta:
        model = Meeting
        fields = ['completed']
