import json

import pika
from django.conf import settings

EXCHANGE = settings.RABBITMQ['EXCHANGE']
PUSHER_QUEUE = settings.RABBITMQ['PUSHER_QUEUE']
SOCKET_QUEUE = settings.RABBITMQ['SOCKET_QUEUE']


class RabbitTestClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ['URI']))
        self.channel = self.connection.channel()

    def get_msgs(self, queue):
        messages = []
        while True:
            method_frame, header_frame, body = self.channel.basic_get(queue, no_ack=True)
            if body is not None:
                messages.append(json.loads(body.decode()))
            else:
                break
        return messages

    def get_meeting_msgs(self):
        return self.get_msgs(SOCKET_QUEUE)

    def clean(self):
        self.channel.queue_purge(queue=PUSHER_QUEUE)
        self.channel.queue_purge(queue=SOCKET_QUEUE)


queue_test_client = RabbitTestClient()
