from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.views import exception_handler
from rest_framework.authentication import TokenAuthentication

from . import tokens


class RedisTokenAuthentication(TokenAuthentication):
    User = get_user_model()

    def authenticate_credentials(self, key):
        a = 10 / 0
        try:
            user_id = tokens.authenticate(key)
            user = self.User.objects.get(pk=user_id)
        except (tokens.AuthenticationFailed, self.User.DoesNotExist):
            raise exceptions.AuthenticationFailed(
                {'error': {'type': '2222', 'status_code': 401, 'description': 'ballbbb'}})
        return user, key
