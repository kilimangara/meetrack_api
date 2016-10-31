from django.conf import settings

import redis

_instance = redis.StrictRedis(host=settings.REDIS['HOST'],
                              port=settings.REDIS['PORT'], db=settings.REDIS['DB'],
                              password=settings.REDIS['PASSWORD'])


def get_instance():
    return _instance
