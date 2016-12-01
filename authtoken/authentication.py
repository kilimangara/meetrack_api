from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from users.models import User
from . import tokens


class RedisTokenAuthentication(TokenAuthentication):
    @classmethod
    def authenticate_credentials(cls, key):
        try:
            user_id = tokens.authenticate(key)
            user = User.objects.get(pk=user_id)
        except (tokens.AuthenticationFailed, User.DoesNotExist):
            raise AuthenticationFailed()
        return user, key
