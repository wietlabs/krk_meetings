import json

from krk_meetings.rabbitmq.RmqHelper import RmqHelper


class RmqConsumer(RmqHelper):
    def __init__(self, exchange, callback_function):
        super().__init__(exchange)
        self.function = callback_function

        if self.exchange_type:
            self.channel.exchange_declare(exchange=self.exchange_name,  exchange_type=self.exchange_type)
        else:
            self.channel.exchange_declare(exchange=self.exchange_name)

        result = self.channel.queue_declare(queue=self.routing_key)
        self.queue = result.method.queue

        self.channel.queue_bind(exchange=self.exchange_name, routing_key=self.routing_key, queue=self.queue)

    def start(self):
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.callback, auto_ack=False)
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        if self.is_heartbeat(json.loads(body)):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        self.function(self.from_json(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)


