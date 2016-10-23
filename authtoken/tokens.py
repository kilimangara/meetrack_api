import binascii
import os

import redis
from django.conf import settings

r = None

TOKEN_KEY = 'token:{}'
USER_KEY = 'user:{}'


class TokenDoesNotExist(Exception):
    pass


class AuthenticationFailed(Exception):
    pass


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


def connect(conn=None):
    global r
    if conn is None:
        r = redis.StrictRedis(max_connections=settings.REDIS['POOL_SIZE'], host=settings.REDIS['HOST'],
                              port=settings.REDIS['PORT'], db=settings.REDIS['DB'])
    else:
        r = conn


def get_token_key(token):
    return TOKEN_KEY.format(token)


def get_user_key(user_id):
    return USER_KEY.format(user_id)


def authenticate(token):
    token_key = get_token_key(token)
    user_id = int(r.get(token_key) or 0)
    if not user_id:
        raise AuthenticationFailed()
    return user_id


def delete(user_id):
    user_key = get_user_key(user_id)
    token = (r.get(user_key) or b'').decode()
    if not token:
        return
    token_key = get_token_key(token)
    r.delete(user_key, token_key)


def create(user_id):
    delete(user_id)
    user_key = get_user_key(user_id)
    token = generate_token()
    token_key = get_token_key(token)
    pipe = r.pipeline()
    pipe.set(user_key, token)
    pipe.set(token_key, user_id)
    pipe.execute()
    return token


connect()
