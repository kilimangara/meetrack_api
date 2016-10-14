from bulk_update.helper import bulk_update
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver

FIELD_MAX_LENGTH = 255


class User(models.Model):
    name = models.CharField(max_length=FIELD_MAX_LENGTH)
    phone = models.CharField(max_length=FIELD_MAX_LENGTH, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    hidden_phone = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to='images/%Y/%m/%d', storage=FileSystemStorage(base_url=settings.STORAGE_URL))
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone'

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

    def add_to_blacklist(self, user_id):
        if self.blocks.filter(user_to_id=user_id).exists():
            self.blocks.filter(user_to_id=user_id).update(active=True)
        else:
            self.blocks.create(user_to_id=user_id)

    def remove_from_blacklist(self, user_id):
        self.blocks.filter(user_to_id=user_id).update(active=False)

    def add_to_contacts(self, phones, names):
        if isinstance(phones, str):
            # if single contact
            input_contacts = {phones: names}
        else:
            input_contacts = dict(zip(phones, names))
        old_contacts = self.contacts.filter(phone__in=input_contacts.keys())
        imported_contacts = []
        for contact in old_contacts:
            phone = contact.phone
            contact.active = True
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
            bulk_update(old_contacts, update_fields=['name', 'active'])
            Contact.objects.bulk_create(to_create)
        return User.objects.filter(id__in=imported_contacts)

    def remove_from_contacts(self, phones):
        self.contacts.filter(phone__in=phones).distinct('phone').update(active=False)

    def blocked_users(self, active_only=True):
        qs = User.objects.filter(inbound_blocks__user_from=self).distinct('id')
        if active_only:
            qs = qs.filter(inbound_blocks__active=True)
        return qs

    def blocked_me(self, active_only=True):
        qs = User.objects.filter(blocks__user_to=self).distinct('id')
        if active_only:
            qs = qs.filter(blocks__active=True)
        return qs

    def contacted_users(self, active_only=True):
        qs = User.objects.filter(inbound_contacts__user_from=self).distinct('id')
        if active_only:
            qs = qs.filter(inbound_contacts__active=True)
        return qs

    def contacted_me(self, active_only=True):
        qs = User.objects.filter(contacts__user_to=self).distinct('id')
        if active_only:
            qs = qs.filter(contacts__active=True)
        return qs


class BlackList(models.Model):
    user_from = models.ForeignKey('User', models.CASCADE, related_name='blocks')
    user_to = models.ForeignKey('User', models.CASCADE, related_name='inbound_blocks')
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user_from', 'user_to']


@receiver(post_save, sender=User)
def new_registered_user(instance, created, **kwargs):
    if not created:
        return
    Contact.objects.filter(phone=instance.phone).update(user_to=instance)


class Contact(models.Model):
    user_from = models.ForeignKey('users.User', models.CASCADE, related_name='contacts')
    user_to = models.ForeignKey('users.User', models.SET_NULL, related_name='inbound_contacts', null=True)
    phone = models.CharField(max_length=FIELD_MAX_LENGTH)
    name = models.CharField(max_length=FIELD_MAX_LENGTH, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user_from', 'user_to']

    def __str__(self):
        return ' '.join([self.phone, str(self.user_from_id)])
