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
    CODE_KEY = 'phone:{}:code'
    ATTEMPTS_KEY = 'phone:{}:attempts'

    def __init__(self, phone):
        self.r = get_redis()
        self.phone = phone
        self.code_key = self.CODE_KEY.format(phone)
        self.attempts_key = self.ATTEMPTS_KEY.format(phone)

    def get_attempts(self):
        return int(self.r.get(self.attempts_key) or 0)

    def set_attempts(self, attempts, time=None):
        pipe = self.r.pipeline()
        pipe.set(self.attempts_key, attempts)
        if time is not None:
            pipe.expire(self.attempts_key, time)
        pipe.execute()

    def increment_attempts(self, time=None):
        count = self.get_attempts()
        if not count:
            self.set_attempts(1, time)
        else:
            self.r.incr(self.attempts_key)
        return count + 1

    def get_code(self):
        code = self.r.get(self.code_key)
        if not code:
            raise PhoneDoesNotExist()
        return code.decode()

    def set_code(self, code, time=None):
        pipe = self.r.pipeline()
        pipe.set(self.code_key, code)
        if time is not None:
            pipe.expire(self.code_key, time)
        pipe.execute()

    def delete(self):
        self.r.delete(self.code_key, self.attempts_key)


def delete_all():
    r = get_redis()
    r.flushdb()


connect()
