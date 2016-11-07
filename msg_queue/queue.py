import json

import redis
from django.conf import settings

SOCKET_QUEUE = 'socket_queue'
PUSHER_QUEUE = 'pusher_queue'

client = None


def connect(fake_client=None):
    global client
    if fake_client is not None:
        client = fake_client
    else:
        client = redis.StrictRedis(host=settings.REDIS['HOST'],
                                   port=settings.REDIS['PORT'], db=settings.REDIS['DB'],
                                   password=settings.REDIS['PASSWORD'])


def send(queue, msg):
    body = json.dumps(msg)
    client.lpush(queue, body)


def send_to_meeting(mid, msg_type, data=None):
    data = data or {}
    send(SOCKET_QUEUE, {
        'meeting': mid,
        'type': msg_type,
        'data': data,
    })


def send_to_users(users, msg):
    send(PUSHER_QUEUE, {
        'users': users,
        'msg': msg,
    })


connect()
