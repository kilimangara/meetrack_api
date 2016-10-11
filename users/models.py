from django.db import models
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import AbstractBaseUser
from django.db.transaction import atomic
from django.conf import settings

FIELD_MAX_LENGTH = 255


class User(models.Model):
    name = models.CharField(max_length=FIELD_MAX_LENGTH)
    phone = models.CharField(max_length=FIELD_MAX_LENGTH, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    hidden_phone = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to='images/%Y/%m/%d', storage=FileSystemStorage(base_url=settings.STORAGE_URL), null=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone'

    blocked_users = models.ManyToManyField('self', related_name='blocked_me', symmetrical=False, through='BlackList',
                                           through_fields=['user_from', 'user_to'])

    def __str__(self):
        return self.phone

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    @property
    def blacklist(self):
        return self.blocked_users.filter(inbound_blocks__active=True)

    def put_into_blacklist(self, user_ids):
        new_ids = set(user_ids) - {self.id}
        exists_ids = set(self.outbound_blocks.values_list('user_to_id', flat=True))
        to_update = new_ids & exists_ids
        to_add = (BlackList(user_from=self, user_to_id=uid) for uid in (new_ids - to_update))
        with atomic():
            self.outbound_blocks.filter(user_to_id__in=to_update).update(active=True)
            self.outbound_blocks.bulk_create(to_add)

    def remove_from_blacklist(self, user_ids):
        self.outbound_blocks.filter(user_to_id__in=user_ids).update(active=False)


class BlackList(models.Model):
    user_from = models.ForeignKey('User', models.CASCADE, related_name='outbound_blocks')
    user_to = models.ForeignKey('User', models.CASCADE, related_name='inbound_blocks')
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user_from', 'user_to']
