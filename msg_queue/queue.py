import json

import pika
from django.conf import settings
from pika import credentials

EXCHANGE = settings.RABBITMQ['EXCHANGE']
PUSHER_KEY = settings.RABBITMQ['PUSHER_KEY']
SOCKET_KEY = settings.RABBITMQ['SOCKET_KEY']
connection = None
channel = None


def connect():
    global connection, channel
    creds = credentials.PlainCredentials(username=settings.RABBITMQ['user'], password=settings.RABBITMQ['password'])
    params = pika.ConnectionParameters(host=settings.RABBITMQ['HOST'], port=settings.RABBITMQ['PORT'],
                                       credentials=creds)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()


def send(routing_key, msg):
    body = json.dumps(msg)
    try:
        channel.publish(EXCHANGE, routing_key, body)
    except:
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
