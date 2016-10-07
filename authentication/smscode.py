import random
import string

import redis
import requests
from django.conf import settings

conn_pool = redis.ConnectionPool(max_connections=settings.REDIS['POOL_SIZE'], host=settings.REDIS['HOST'],
                                 port=settings.REDIS['PORT'], db=settings.REDIS['DB'])
CODE_LENGTH = 5
PHONE_KEY = 'phone:{}'


class LimitExceededError(Exception):
    pass


class ValidationError(Exception):
    pass


def generate_code():
    return ''.join(random.choice(string.digits) for _ in range(CODE_LENGTH))


def send_sms(phone, code):
    r = requests.post(settings.SMS_AUTH['REQUEST_URL'],
                      data={'To': phone, 'From': settings.SMS_AUTH['FROM_NUMBER'], 'Body': code},
                      auth=(settings.SMS_AUTH['ACCOUNT_SID'], settings.SMS_AUTH['AUTH_TOKEN']))
    if r.status_code != 201:
        raise Exception("SMS sending fails")


def new(phone):
    code = generate_code()
    r = redis.StrictRedis(connection_pool=conn_pool)
    key = PHONE_KEY.format(phone)
    count = int(r.hget(key, 'attempts') or 0)
    if count >= settings.SMS_AUTH['ATTEMPTS_LIMIT']:
        raise LimitExceededError()
    r.hmset(key, {'code': code, 'attempts': count + 1})
    send_sms(phone, code)
    r.pexpire(key, settings.SMS_AUTH['LIFE_TIME'])


def validate(phone, code):
    r = redis.StrictRedis(connection_pool=conn_pool)
    key = PHONE_KEY.format(phone)
    real_code, count = r.hmget(key, ['code', 'attempts'])
    if real_code is None or count is None:
        raise ValidationError()
    real_code = real_code.decode()
    count = int(count)
    if count >= settings.SMS_AUTH['ATTEMPTS_LIMIT']:
        raise LimitExceededError()
    if code != real_code:
        r.hset(key, 'attempts', count + 1)
        raise ValidationError()
    r.delete(key)
