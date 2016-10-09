import binascii
import os

import redis
from django.conf import settings

conn_pool = redis.ConnectionPool(max_connections=settings.REDIS['POOL_SIZE'], host=settings.REDIS['HOST'],
                                 port=settings.REDIS['PORT'], db=settings.REDIS['DB'])

TOKEN_KEY = 'token:{}'
USER_KEY = 'user:{}'


class TokenDoesNotExist(Exception):
    pass


class AuthenticationFailed(Exception):
    pass


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


def get_redis():
    return redis.StrictRedis(connection_pool=conn_pool)


def get_token_key(token):
    return TOKEN_KEY.format(token)


def get_user_key(user_id):
    return USER_KEY.format(user_id)


def authenticate(token):
    r = get_redis()
    token_key = get_token_key(token)
    user_id = int(r.get(token_key) or 0)
    if not user_id:
        raise AuthenticationFailed()
    user_key = get_user_key(user_id)
    token_redis = (r.get(user_key) or b'').decode()
    if token_redis != token:
        pipe = r.pipeline()
        pipe.delete(token_key)
        pipe.delete(user_key)
        pipe.execute()
        raise AuthenticationFailed()
    return user_id


def get(user_id):
    r = get_redis()
    user_key = get_user_key(user_id)
    token = (r.get(user_key) or b'').decode()
    if token:
        token_key = get_token_key(token)
        user_id_redis = int(r.get(token_key) or 0)
        if user_id == user_id_redis:
            return token
        pipe = r.pipeline()
        pipe.delete(token_key)
        pipe.delete(user_key)
        pipe.execute()
    raise TokenDoesNotExist()


def create(user_id):
    r = get_redis()
    user_key = get_user_key(user_id)
    token = generate_token()
    token_key = get_token_key(token)
    pipe = r.pipeline()
    pipe.set(user_key, token)
    pipe.set(token_key, user_id)
    pipe.execute()
    return token


def get_or_create(user_id):
    try:
        token = get(user_id)
    except TokenDoesNotExist:
        token = create(user_id)
    return token
