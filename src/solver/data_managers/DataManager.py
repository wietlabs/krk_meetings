from abc import abstractmethod
from threading import Lock
from threading import Thread

from src.exchanges import EXCHANGES
from src.data_provider.FloydDataProvider import FloydDataProvider
from src.rabbitmq.RmqConsumer import RmqConsumer


class DataManager:
    def __init__(self) -> None:
        self.data = None
        self.up_to_date = True
        self.lock = Lock()
        self.data_consumer = RmqConsumer(EXCHANGES.FLOYD_DATA.value, self.update_data)
        self.data_consumer_thread = Thread(target=self.data_consumer.start, args=[])

    def start(self) -> None:
        self.update_data()
        self.data_consumer_thread.start()

    def stop(self) -> None:
        self.data_consumer_thread.start.do_run = False

    def update_data(self) -> None:
        data = self.get_data()
        with self.lock:
            self.data = data
            self.up_to_date = False

    def get_updated_data(self) -> dict:
        with self.lock:
            self.up_to_date = True
            return self.data

    @abstractmethod
    def get_data(self) -> dict:
        while False:
            yield None
