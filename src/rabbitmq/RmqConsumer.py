import json

import pika


class RmqConsumer:
    def __init__(self, exchange, callback_function):
        self.exchange_name, self.exchange_type, self.routing_key, _, self.from_json = exchange
        self.function = callback_function

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        if self.exchange_type:
            self.channel.exchange_declare(exchange=self.exchange_name,  exchange_type=self.exchange_type)
        else:
            self.channel.exchange_declare(exchange=self.exchange_name)

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue = result.method.queue

        self.channel.queue_bind(exchange=self.exchange_name, routing_key=self.routing_key, queue=self.queue)

    def start(self):
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.callback, auto_ack=False)
        self.channel.start_consuming()

    def stop(self):
        self.connection.close()

    def callback(self, ch, method, properties, body):
        self.function(self.from_json(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)


