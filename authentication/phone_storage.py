import redis
from django.conf import settings

conn_pool = None


class PhoneDoesNotExist(Exception):
    pass


def get_redis():
    return redis.StrictRedis(connection_pool=conn_pool)


def connect():
    global conn_pool
    conn_pool = redis.ConnectionPool(max_connections=settings.REDIS['POOL_SIZE'], host=settings.REDIS['HOST'],
                                     port=settings.REDIS['PORT'], db=settings.REDIS['DB'])


class Phone(object):
    PHONE_KEY = 'phone:{}'

    def __init__(self, phone):
        self.r = get_redis()
        self.phone = phone
        self.key = self.PHONE_KEY.format(phone)

    def get_attempts(self):
        return int(self.r.hget(self.key, 'attempts') or 0)

    def get(self):
        code, attempts = self.r.hmget(self.key, ['code', 'attempts'])
        if code is None or attempts is None:
            raise PhoneDoesNotExist()
        code = code.decode()
        attempts = int(attempts)
        return code, attempts

    def delete(self):
        self.r.delete(self.key)

    def set_attempts(self, attempts):
        self.r.hset(self.key, 'attempts', attempts)

    def create(self, code, attempts=None, time=None):
        pipe = self.r.pipeline()
        if attempts is None:
            attempts = self.get_attempts() + 1
        pipe.hmset(self.key, {'code': code, 'attempts': attempts})
        if time is not None:
            pipe.pexpire(self.key, time)
        pipe.execute()


def delete_all():
    r = get_redis()
    r.flushdb()


connect()
