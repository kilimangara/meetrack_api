import random

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User

FIELD_MAX_LENGTH = 255


class Meeting(models.Model):
    king = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, related_name='kingdoms', null=True)
    title = models.CharField(max_length=FIELD_MAX_LENGTH)
    description = models.TextField()
    logo = models.ImageField(upload_to='images/%Y/%m/%d', storage=FileSystemStorage(base_url=settings.STORAGE_URL))
    time = models.DateTimeField()

    def leave(self, user_id, save=True):
        self.members.filter(user_id=user_id).update(active=False)
        users = self.users().exclude(id=user_id)
        if users:
            if self.king_id == user_id:
                self.king = random.choice(users)
            else:
                return
        else:
            self.king = None
        if save:
            self.save(update_fields=['king'])

    def users(self, active_only=True):
        qs = User.objects.filter(memberships__meeting=self).distinct('id')
        if active_only:
            qs = qs.filter(memberships__active=True)
        return qs


@receiver(post_save, sender=Meeting)
def new_meeting(instance, created, **kwargs):
    if not created:
        return
    instance.members.create(user=instance.king)


class Member(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='memberships')
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE, related_name='members')
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'meeting']
