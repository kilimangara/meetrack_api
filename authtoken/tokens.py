import binascii
import os

import redis
from django.conf import settings

client = None


def connect(fake_client=None):
    global client

    global client
    if fake_client is not None:
        client = fake_client
    else:
        client = redis.StrictRedis(host=settings.REDIS['HOST'],
                                   port=settings.REDIS['PORT'], db=settings.REDIS['DB'],
                                   password=settings.REDIS['PASSWORD'])


class TokenDoesNotExist(Exception):
    pass


class AuthenticationFailed(Exception):
    pass


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


def get_token_key(token):
    return 'token:{}'.format(token)


def get_user_key(user_id):
    return 'user:{}'.format(user_id)


def authenticate(token):
    token_key = get_token_key(token)
    user_id = int(client.get(token_key) or 0)
    if not user_id:
        raise AuthenticationFailed()
    return user_id


def delete(user_id):
    user_key = get_user_key(user_id)
    token = (client.get(user_key) or b'').decode()
    if not token:
        return
    token_key = get_token_key(token)
    client.delete(user_key, token_key)


def create(user_id):
    delete(user_id)
    user_key = get_user_key(user_id)
    token = generate_token()
    token_key = get_token_key(token)
    pipe = client.pipeline()
    pipe.set(user_key, token)
    pipe.set(token_key, user_id)
    pipe.execute()
    return token
