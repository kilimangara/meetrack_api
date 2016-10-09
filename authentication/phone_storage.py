import redis
from django.conf import settings


class PhoneDoesNotExist(Exception):
    pass


class Phone(object):
    PHONE_KEY = 'phone:{}'
    conn_pool = redis.ConnectionPool(max_connections=settings.REDIS['POOL_SIZE'], host=settings.REDIS['HOST'],
                                     port=settings.REDIS['PORT'], db=settings.REDIS['DB'])

    def __init__(self, phone):
        self.r = redis.StrictRedis(connection_pool=self.conn_pool)
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
        if time:
            pipe.pexpire(self.key, time)
        pipe.execute()
