import binascii
import os

from redis_app.redis import get_instance

redis = get_instance()


def set_db(db):
    global redis
    redis = db


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
    user_id = int(redis.get(token_key) or 0)
    if not user_id:
        raise AuthenticationFailed()
    return user_id


def delete(user_id):
    user_key = get_user_key(user_id)
    token = (redis.get(user_key) or b'').decode()
    if not token:
        return
    token_key = get_token_key(token)
    redis.delete(user_key, token_key)


def create(user_id):
    delete(user_id)
    user_key = get_user_key(user_id)
    token = generate_token()
    token_key = get_token_key(token)
    pipe = redis.pipeline()
    pipe.set(user_key, token)
    pipe.set(token_key, user_id)
    pipe.execute()
    return token
