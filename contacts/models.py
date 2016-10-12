from django.db import models
from bulk_update.manager import BulkUpdateManager

FIELD_MAX_LENGTH = 255


class Contact(models.Model):
    owner = models.ForeignKey('users.User', models.CASCADE, related_name='contacts')
    to = models.ForeignKey('users.User', models.SET_NULL, related_name='inbound_contacts', null=True)
    phone = models.CharField(max_length=FIELD_MAX_LENGTH)
    name = models.CharField(max_length=FIELD_MAX_LENGTH, null=True)
    active = models.BooleanField(default=True)
    objects = BulkUpdateManager()

    class Meta:
        unique_together = ['owner', 'to']

    def __str__(self):
        return ' '.join([self.phone, str(self.owner_id)])
