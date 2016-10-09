from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from . import token_storage


class RedisTokenAuthentication(TokenAuthentication):
    User = get_user_model()

    def authenticate_credentials(self, key):
        try:
            user_id = token_storage.authenticate(key)
            user = self.User.objects.get(pk=user_id)
        except (token_storage.AuthenticationFailed, self.User.DoesNotExist):
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        return user, key
