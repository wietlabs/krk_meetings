from threading import Thread
import pika

from src.rabbitmq.RmqHelper import RmqHelper


class RmqProducer(RmqHelper):
    def __init__(self, exchange):
        super().__init__(exchange)
        self.heartbeat_thread = self.data_consumer_thread = Thread(target=self.set_heartbeat_scheduler, args=[])
        self.heartbeat_thread.start()

        if self.exchange_type:
            self.channel.exchange_declare(exchange=self.exchange_name,  exchange_type=self.exchange_type)
        else:
            self.channel.exchange_declare(exchange=self.exchange_name)

    def stop(self):
        self.connection.close()

    def send_msg(self, message, lost_stream_msg="Rabbitmq error: Stream connection lost"):
        try:
            self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=self.to_json(message))
        except pika.exceptions.StreamLostError:
            print(lost_stream_msg)

    def send_error(self, message, lost_stream_msg="Rabbitmq error: Stream connection lost"):
        try:
            self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=message)
        except pika.exceptions.StreamLostError:
            print(lost_stream_msg)

    def callback(self, ch, method, properties, body):
        pass


