import random

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.transaction import atomic

from users.models import User

FIELD_MAX_LENGTH = 255


class Meeting(models.Model):
    title = models.CharField(max_length=FIELD_MAX_LENGTH)
    description = models.TextField(null=True)
    logo = models.ImageField(upload_to='images/%Y/%m/%d', storage=FileSystemStorage(base_url=settings.STORAGE_URL))
    created_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    users = models.ManyToManyField('users.User', related_name='meetings', through='Member')
    destination_lat = models.FloatField(default=0.0)
    destination_lon = models.FloatField(default=0.0)

    @property
    def king_id(self):
        return User.objects.filter(
            memberships__meeting=self, memberships__king=True).values_list('id', flat=True).first()

    def remove_user(self, user_id):
        meeting_exists = True
        with atomic():
            if self.members.filter(user_id=user_id, king=True).exists():
                user_ids = self.members.exclude(user_id=user_id).values_list('user_id', flat=True)
                if user_ids:
                    new_king_id = random.choice(user_ids)
                    self.members.filter(user_id=new_king_id).update(king=True)
            deleted_count, _ = self.members.filter(user_id=user_id).delete()
            removed = bool(deleted_count)
            if not self.members.exists():
                self.delete()
                meeting_exists = False
        return removed, meeting_exists

    def add_user(self, user_id):
        _, created = self.members.get_or_create(user_id=user_id)
        return created

    def __str__(self):
        return str(self.id)


class Member(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='memberships')
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE, related_name='members')
    king = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'meeting']
