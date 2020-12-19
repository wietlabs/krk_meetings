from abc import abstractmethod
from threading import Lock
from threading import Thread
from krk_meetings.rabbitmq.RmqConsumer import RmqConsumer
import time


class DataManager:
    def __init__(self) -> None:
        self.data = None
        self.data_loaded = False
        self.last_data_update = time.time()
        self.lock = Lock()
        self.data_consumer = None
        self.data_consumer_thread = None
        self.up_to_date = True

    def start(self) -> None:
        self.data_consumer = RmqConsumer(self.exchange, self.handle_message)
        self.data_consumer_thread = Thread(target=self.data_consumer.start, args=[])
        self.data_consumer_thread.start()
        try:
            self.data = self.get_data()
            self.up_to_date = False
            self.data_loaded = True
        except FileNotFoundError:
            pass

    def stop(self) -> None:
        self.data_consumer_thread.start.do_run = False

    @abstractmethod
    def handle_message(self, msg) -> None:
        while False:
            yield None

    def update_data(self) -> None:
        data = self.get_data()
        with self.lock:
            self.data = data
            self.up_to_date = False
            self.data_loaded = True

    def get_updated_data(self) -> dict:
        with self.lock:
            self.up_to_date = True
            return self.data

    @property
    @abstractmethod
    def exchange(self):
        while False:
            yield None

    @abstractmethod
    def get_data(self) -> dict:
        while False:
            yield None
