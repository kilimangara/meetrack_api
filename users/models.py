from django.db import models
from django.contrib.auth.models import AbstractBaseUser

FIELD_MAX_LENGTH = 255


class User(models.Model):
    name = models.CharField(max_length=FIELD_MAX_LENGTH)
    phone = models.CharField(max_length=FIELD_MAX_LENGTH, unique=True)
    created = models.DateTimeField(auto_now_add=True)
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
