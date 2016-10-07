import binascii
import os

import redis
from django.conf import settings

conn_pool = redis.ConnectionPool(max_connections=settings.REDIS['POOL_SIZE'], host=settings.REDIS['HOST'],
                                 port=settings.REDIS['PORT'], db=settings.REDIS['DB'])

TOKEN_KEY = 'token:{}'
USER_KEY = 'user:{}'


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


def authorize(token):
    pass


def get_or_create(user_id):
    r = redis.StrictRedis(connection_pool=conn_pool)
    user_key = USER_KEY.format(user_id)
    token = (r.get(user_key) or b'').decode()
    if token:
        token_key = TOKEN_KEY.format(token)
        user_id_redis = int(r.get(token_key) or 0)
        if user_id == user_id_redis:
            return token
        r.delete(token_key)
    token = generate_token()
    token_key = TOKEN_KEY.format(token)
    pipe = r.pipeline()
    pipe.set(user_key, token)
    pipe.set(token_key, user_id)
    pipe.execute()
    return token
