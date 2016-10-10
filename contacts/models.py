from django.db import models

FIELD_MAX_LENGTH = 255


class Contact(models.Model):
    owner = models.ForeignKey('users.User', models.CASCADE, related_name='contacts')
    to = models.ForeignKey('users.User', models.SET_NULL, related_name='other_contacts', null=True)
    phone = models.CharField(max_length=FIELD_MAX_LENGTH)
    name = models.CharField(max_length=FIELD_MAX_LENGTH, null=True)

    class Meta:
        unique_together = ['owner', 'to']
