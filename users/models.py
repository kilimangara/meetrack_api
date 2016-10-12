from bulk_update.helper import bulk_update
from bulk_update.manager import BulkUpdateManager
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.transaction import atomic

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

    def put_into_blacklist(self, user_ids):
        new_ids = set(user_ids) - {self.id}
        exists_ids = set(self.blocks.values_list('user_to_id', flat=True))
        to_update = new_ids & exists_ids
        to_add = (BlackList(user_from=self, user_to_id=uid) for uid in (new_ids - to_update))
        with atomic():
            self.blocks.filter(user_to_id__in=to_update).update(active=True)
            self.blocks.bulk_create(to_add)

    def remove_from_blacklist(self, user_ids):
        self.blocks.filter(user_to_id__in=user_ids).update(active=False)

    def import_contacts(self, phones, names):
        input_contacts = dict(zip(phones, names))
        old_contacts = self.contacts.filter(phone__in=input_contacts.keys())
        imported_contacts = []
        for contact in old_contacts:
            phone = contact.phone
            contact.active = True
            contact.name = input_contacts[phone]
            input_contacts.pop(phone)
            if contact.to_id is not None:
                imported_contacts.append(contact.to_id)
        registered_phones = dict(User.objects.filter(phone__in=input_contacts.keys()).values_list('phone', 'id'))
        to_create = []
        for phone, name in input_contacts.items():
            to_id = registered_phones.get(phone, None)
            c = Contact(owner=self, to_id=to_id, phone=phone, name=name)
            to_create.append(c)
            if to_id is not None:
                imported_contacts.append(c.to_id)
        with atomic():
            bulk_update(old_contacts, update_fields=['name', 'active'])
            Contact.objects.bulk_create(to_create)
        return User.objects.filter(id__in=imported_contacts)

    def delete_contacts(self, phones):
        contacts = self.contacts.filter(phone__in=phones).distinct('phone')
        for c in contacts:
            c.active = False
        bulk_update(contacts, update_fields=['active'])

    def blocked_users(self, active=True):
        return User.objects.filter(inbound_blocks__user_from=self, inbound_blocks__active=active)

    def blocked_me(self, active=True):
        return User.objects.filter(outbound_blocks__user_to=self, outbount_blocks__active=active)

    def contacted_users(self, active=True):
        return User.objects.filter(inbound_contacts__user_to=self, inbound_contacts__active=active)

    def contacted_me(self, active=True):
        return User.objects.filter(outbound_contacts__user_to=self, outbount_contacts__active=active)


class BlackList(models.Model):
    user_from = models.ForeignKey('User', models.CASCADE, related_name='blocks')
    user_to = models.ForeignKey('User', models.CASCADE, related_name='inbound_blocks')
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user_from', 'user_to']


class Contact(models.Model):
    owner = models.ForeignKey('users.User', models.CASCADE, related_name='contacts')
    to = models.ForeignKey('users.User', models.SET_NULL, related_name='inbound_contacts', null=True)
    phone = models.CharField(max_length=FIELD_MAX_LENGTH)
    name = models.CharField(max_length=FIELD_MAX_LENGTH, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['owner', 'to']

    def __str__(self):
        return ' '.join([self.phone, str(self.owner_id)])
