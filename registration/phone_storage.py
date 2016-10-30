from redis_app.redis import get_instance

redis = get_instance()


def set_db(db):
    global redis
    redis = db


class PhoneDoesNotExist(Exception):
    pass


class Phone(object):
    CODE_KEY = 'phone:{}:code'
    ATTEMPTS_KEY = 'phone:{}:attempts'

    def __init__(self, phone):
        self.r = redis
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
