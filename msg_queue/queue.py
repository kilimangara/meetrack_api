import pika
from pika.exceptions import ConnectionClosed
import json
from django.conf import settings

EXCHANGE = settings.RABBITMQ['EXCHANGE']
PUSHER_KEY = settings.RABBITMQ['PUSHER_KEY']
SOCKET_KEY = settings.RABBITMQ['SOCKET_KEY']
connection = None
channel = None


def connect():
    global connection, channel
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ['URI']))
    channel = connection.channel()


def send(routing_key, msg):
    body = json.dumps(msg)
    try:
        channel.publish(EXCHANGE, routing_key, body)
    except ConnectionClosed:
        connect()
        channel.publish(EXCHANGE, routing_key, body)


def send_to_meeting(mid, msg):
    send(SOCKET_KEY, {
        'meeting': mid,
        'msg': msg,
    })


def send_to_users(users, msg):
    send(PUSHER_KEY, {
        'users': users,
        'msg': msg,
    })


connect()
