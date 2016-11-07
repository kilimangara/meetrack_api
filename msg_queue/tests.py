import json

import redis
from django.conf import settings

from .queue import SOCKET_QUEUE, PUSHER_QUEUE


class QueueTestConsumer(object):
    def __init__(self, redis_client=None):
        if redis_client is not None:
            self.r = redis_client
        else:
            self.r = redis.StrictRedis(host=settings.REDIS['HOST'],
                                       port=settings.REDIS['PORT'], db=settings.REDIS['DB'],
                                       password=settings.REDIS['PASSWORD'])

    def get_msgs(self, queue):
        messages = []
        body = self.r.rpop(queue)
        while body is not None:
            messages.append(json.loads(body.decode()))
            body = self.r.rpop(queue)
        return messages

    def get_meeting_msgs(self):
        return self.get_msgs(SOCKET_QUEUE)

    def clean(self):
        self.r.delete(PUSHER_QUEUE)
        self.r.delete(SOCKET_QUEUE)
