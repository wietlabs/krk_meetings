from threading import Thread
import pika

from krk_meetings.exchanges import Exchange
from krk_meetings.rabbitmq.RmqHelper import RmqHelper


class RmqProducer(RmqHelper):
    def __init__(self, exchange: Exchange):
        super().__init__(exchange)
        self.heartbeat_thread = self.data_consumer_thread = Thread(target=self.set_heartbeat_scheduler, args=[])
        if self.exchange.type:
            self.channel.exchange_declare(exchange=self.exchange.name, exchange_type=self.exchange.type)
        else:
            self.channel.exchange_declare(exchange=self.exchange.name)

    def start(self):
        self.heartbeat_thread.start()


