from threading import Thread, Lock

import pika
import sched
import time
import json

HEARTBEAT_MSG = "HEARTBEAT"


class RmqHelper:
    def __init__(self, exchange):
        self.exchange_name, self.exchange_type, self.routing_key, self.to_json, self.from_json = exchange
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
        self.channel = self.connection.channel()
        self.alive = True
        self.lock = Lock()

    def stop(self):
        if self.connection.is_open:
            self.connection.close()
        self.alive = False

    def send_msg(self, message, lost_stream_msg="Rabbitmq error: Stream connection lost"):
        try:
            self.lock.acquire()
            self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=self.to_json(message))
            self.lock.release()
        except pika.exceptions.StreamLostError:
            print(f"{lost_stream_msg} {self.routing_key}")

    def send_heartbeat(self, lost_stream_msg="Rabbitmq error: Stream connection lost on"):
        try:
            self.lock.acquire()
            self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key,
                                       body=json.dumps(HEARTBEAT_MSG))
            self.lock.release()
        except pika.exceptions.StreamLostError:
            print(f"{lost_stream_msg} HEARTBEAT on {self.routing_key}")

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
