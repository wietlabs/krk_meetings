from threading import Lock

import pika
import sched
import time
import json

from krk_meetings.exchanges import Exchange
from krk_meetings.logger import get_logger

logger = get_logger(__name__)

HEARTBEAT_MSG = "HEARTBEAT"


class RmqHelper:
    def __init__(self, exchange: Exchange):
        self.exchange = exchange
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='10.0.0.20', heartbeat=600))
        self.channel = self.connection.channel()
        self.alive = True
        self.lock = Lock()

    def stop(self):
        if self.connection.is_open:
            self.connection.close()
        self.alive = False

    def send_msg(self, message, lost_stream_msg="Rabbitmq error: Stream connection lost"):
        self.lock.acquire()
        try:
            self.channel.basic_publish(exchange=self.exchange.name, routing_key=self.exchange.key, body=self.exchange.to_json(message))
        except pika.exceptions.StreamLostError:
            logger.warn(f"{lost_stream_msg} {self.exchange.key}")
        finally:
            self.lock.release()

    def send_heartbeat(self, lost_stream_msg="Rabbitmq error: Stream connection lost on"):
        try:
            self.lock.acquire()
            self.channel.basic_publish(exchange=self.exchange.name, routing_key=self.exchange.key,
                                       body=json.dumps(HEARTBEAT_MSG))
            self.lock.release()
        except pika.exceptions.StreamLostError:
            logger.warn(f"{lost_stream_msg} HEARTBEAT on {self.exchange.key}")

    @staticmethod
    def is_heartbeat(message):
        return message == HEARTBEAT_MSG

    def set_heartbeat_scheduler(self):
        heartbeat_scheduler = sched.scheduler(time.time, time.sleep)

        def scheduler_loop(h_s):
            self.send_heartbeat()
            if self.alive:
                heartbeat_scheduler.enter(10, 1, scheduler_loop, (h_s,))

        heartbeat_scheduler.enter(10, 1, scheduler_loop, (heartbeat_scheduler,))
        heartbeat_scheduler.run()
