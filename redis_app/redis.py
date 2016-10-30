from django.conf import settings

import redis

_instance = redis.StrictRedis(max_connections=settings.REDIS['POOL_SIZE'], host=settings.REDIS['HOST'],
                              port=settings.REDIS['PORT'], db=settings.REDIS['DB'],
                              password=settings.REDIS['PASSWORD'])


def get_instance():
    return _instance
