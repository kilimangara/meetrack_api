from collections import Iterable

from bulk_update.helper import bulk_update
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.db.transaction import atomic
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

from authtoken import tokens

FIELD_MAX_LENGTH = 255


class User(models.Model):
    name = models.CharField(max_length=FIELD_MAX_LENGTH)
    phone = PhoneNumberField(max_length=FIELD_MAX_LENGTH, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hidden_phone = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='images/%Y/%m/%d', storage=FileSystemStorage(base_url=settings.STORAGE_URL))
    blocked_users = models.ManyToManyField('self', related_name='blocked_me', symmetrical=False, through='BlackList',
                                           through_fields=['user_from', 'user_to'])
    contacted_users = models.ManyToManyField('self', related_name='contacted_me', symmetrical=False, through='Contact',
                                             through_fields=['user_from', 'user_to'])

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone'

    def __str__(self):
        return self.phone + ' ' + str(self.id)

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

    def add_to_blacklist(self, user_id):
        self.blocks.get_or_create(user_to_id=user_id)

    def remove_from_blacklist(self, user_id):
        self.blocks.filter(user_to_id=user_id).delete()

    def add_to_contacts(self, phones, names):
        if isinstance(phones, Iterable) and not isinstance(phones, str):
            # if single contact
            input_contacts = dict(zip(phones, names))
        else:
            input_contacts = {phones: names}
        old_contacts = self.contacts.filter(phone__in=input_contacts.keys())
        imported_contacts = []
        for contact in old_contacts:
            phone = contact.phone
            contact.name = input_contacts[phone]
            input_contacts.pop(phone)
            if contact.user_to_id is not None:
                imported_contacts.append(contact.user_to_id)
        registered_phones = dict(User.objects.filter(phone__in=input_contacts.keys()).values_list('phone', 'id'))
        to_create = []
        for phone, name in input_contacts.items():
            user_to_id = registered_phones.get(phone, None)
            c = Contact(user_from=self, user_to_id=user_to_id, phone=phone, name=name)
            to_create.append(c)
            if user_to_id is not None:
                imported_contacts.append(c.user_to_id)
        with atomic():
            bulk_update(old_contacts, update_fields=['name'])
            Contact.objects.bulk_create(to_create)
        return User.objects.filter(id__in=imported_contacts)

    def remove_from_contacts(self, phones):
        self.contacts.filter(phone__in=phones).distinct('phone').delete()


class BlackList(models.Model):
    user_from = models.ForeignKey('User', models.CASCADE, related_name='blocks')
    user_to = models.ForeignKey('User', models.CASCADE, related_name='inbound_blocks')

    class Meta:
        unique_together = ['user_from', 'user_to']


@receiver(post_save, sender=User)
def new_registered_user(instance, created, **kwargs):
    if not created:
        return
    Contact.objects.filter(phone=instance.phone).update(user_to=instance)


@receiver(pre_delete, sender=User)
def delete_user(instance, **kwargs):
    tokens.delete(instance.id)
    meetings = instance.meetings.all()
    for m in meetings:
        m.leave(instance.id)


class Contact(models.Model):
    user_from = models.ForeignKey('User', models.CASCADE, related_name='contacts')
    user_to = models.ForeignKey('User', models.SET_NULL, related_name='inbound_contacts', null=True)
    phone = models.CharField(max_length=FIELD_MAX_LENGTH)
    name = models.CharField(max_length=FIELD_MAX_LENGTH, null=True)

    class Meta:
        unique_together = ['user_from', 'user_to']

    def __str__(self):
        return ' '.join([self.phone, str(self.user_from_id)])
