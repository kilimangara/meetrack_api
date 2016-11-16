import redis
from django.conf import settings

client = None


def connect(fake_client=None):
    global client
    if fake_client is not None:
        client = fake_client
    else:
        client = redis.StrictRedis(host=settings.REDIS['HOST'],
                                   port=settings.REDIS['PORT'], db=settings.REDIS['DB'],
                                   password=settings.REDIS['PASSWORD'])


class PhoneStorage(object):
    CODE_KEY = 'phone:{}:code'
    ATTEMPTS_KEY = 'phone:{}:attempts'

    class DoesNotExist(Exception):
        pass

    def __init__(self, phone):
        self.r = client
        self.phone = phone
        self.code_key = self.CODE_KEY.format(phone)
        self.attempts_key = self.ATTEMPTS_KEY.format(phone)

    def get_attempts(self):
        pipe = self.r.pipeline()
        pipe.get(self.attempts_key)
        pipe.ttl(self.attempts_key)
        results = pipe.execute()
        attempts_count = int(results[0] or 0)
        wait_time = results[1] if results[1] >= 0 else None
        return attempts_count, wait_time

    def set_attempts(self, attempts, lifetime=None):
        if lifetime is None:
            self.r.set(self.attempts_key, attempts)
        else:
            pipe = self.r.pipeline()
            pipe.set(self.attempts_key, attempts)
            pipe.expire(self.attempts_key, lifetime)
            pipe.execute()

    def increment_attempts(self):
        return self.r.incr(self.attempts_key)

    def get_code(self):
        code = self.r.get(self.code_key)
        if not code:
            raise self.DoesNotExist()
        return code.decode()

    def set_code(self, code, lifetime=None):
        if lifetime is None:
            self.r.set(self.code_key, code)
        else:
            pipe = self.r.pipeline()
            pipe.set(self.code_key, code)
            pipe.expire(self.code_key, lifetime)
            pipe.execute()

    def delete_code(self):
        self.r.delete(self.code_key)


connect()
