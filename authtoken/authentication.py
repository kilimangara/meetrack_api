from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from . import tokens


class RedisTokenAuthentication(TokenAuthentication):
    User = get_user_model()

    def authenticate_credentials(self, key):
        try:
            user_id = tokens.authenticate(key)
            user = self.User.objects.get(pk=user_id)
        except (tokens.AuthenticationFailed, self.User.DoesNotExist):
            raise AuthenticationFailed()
        return user, key
