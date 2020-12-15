from threading import Thread
import pika

from krk_meetings.rabbitmq.RmqHelper import RmqHelper


class RmqProducer(RmqHelper):
    def __init__(self, exchange):
        super().__init__(exchange)
        self.heartbeat_thread = self.data_consumer_thread = Thread(target=self.set_heartbeat_scheduler, args=[])
        if self.exchange_type:
            self.channel.exchange_declare(exchange=self.exchange_name,  exchange_type=self.exchange_type)
        else:
            self.channel.exchange_declare(exchange=self.exchange_name)

    def start(self):
        self.heartbeat_thread.start()


