import json

from krk_meetings.exchanges import Exchange
from krk_meetings.rabbitmq.RmqHelper import RmqHelper


class RmqConsumer(RmqHelper):
    def __init__(self, exchange: Exchange, callback_function):
        super().__init__(exchange)
        self.function = callback_function

        if self.exchange.type:
            self.channel.exchange_declare(exchange=self.exchange.name, exchange_type=self.exchange.type)
        else:
            self.channel.exchange_declare(exchange=self.exchange.name)
        queue_name = f"{self.exchange.queue}_{str(id(self))}" if self.exchange.separate_instances else self.exchange.queue
        result = self.channel.queue_declare(queue=queue_name)
        self.queue = result.method.queue

        self.channel.queue_bind(exchange=self.exchange.name, routing_key=self.exchange.key, queue=self.queue)

    def start(self):
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.callback, auto_ack=False)
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        if self.is_heartbeat(json.loads(body)):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        self.function(self.exchange.from_json(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)


