import random

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.transaction import atomic
from django.db import models

from users.models import User

FIELD_MAX_LENGTH = 255


class Meeting(models.Model):
    title = models.CharField(max_length=FIELD_MAX_LENGTH)
    description = models.TextField()
    logo = models.ImageField(upload_to='images/%Y/%m/%d', storage=FileSystemStorage(base_url=settings.STORAGE_URL))
    created = models.DateTimeField(auto_now_add=True)
    time = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)

    @property
    def king(self):
        qs = self.users
        # print(User.objects.filter(memberships__meeting=self).distinct('id').filter(memberships__active=True).filter(
        #     memberships__king=True))
        print(qs)
        print(qs.filter(memberships__king=True))
        return self.users.filter(memberships__king=True).first()

    def leave(self, user_id):
        with atomic():
            if self.members.filter(user_id=user_id, king=True).exists():
                user_ids = self.members.filter(active=True).exclude(user_id=user_id).values_list('user_id', flat=True)
                if user_ids:
                    new_king_id = random.choice(user_ids)
                    self.members.filter(user_id=new_king_id).update(king=True)
            self.members.filter(user_id=user_id).update(active=False, king=False)

    def exclude(self, user_id):
        self.members.filter(user_id=user_id).update(active=False)

    def invite(self, user_id):
        if self.members.filter(user_id=user_id).exists():
            self.members.filter(user_id=user_id).update(active=True)
        else:
            self.members.create(user_id=user_id)

    @property
    def users(self):
        qs = User.objects.filter(memberships__meeting=self).distinct('id')
        qs = qs.filter(memberships__active=True)
        return qs

    def __str__(self):
        return str(self.id)


class Member(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='memberships')
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE, related_name='members')
    active = models.BooleanField(default=True)
    king = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'meeting']
