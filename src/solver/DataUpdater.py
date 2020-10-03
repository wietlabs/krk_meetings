from threading import Lock
from threading import Thread

from src.config import EXCHANGES
from src.data_provider.FloydDataProvider import FloydDataProvider
from src.rabbitmq.RmqConsumer import RmqConsumer


class DataUpdater:
    def __init__(self):
        self.graph = None
        self.kernelized_graph = None
        self.distances = None
        self.stops_df = None
        self.routes_df = None
        self.stops_df_by_name = None
        self.stop_times_0 = None
        self.stop_times_24 = None
        self.paths = None
        self.day_to_services_dict = None
        self.lock = Lock()
        self.data_consumer = RmqConsumer(EXCHANGES.FLOYD_DATA.value, self.update_data)
        self.data_consumer_thread = Thread(target=self.data_consumer.start, args=[])

    def start(self):
        self.update_data()
        self.data_consumer_thread.start()

    def stop(self):
        self.data_consumer_thread.start.do_run = False

    def update_data(self):
        data = FloydDataProvider.load_floyd_data()
        if data is None:
            return
        with self.lock:
            self.graph = data.graph
            self.kernelized_graph = data.kernelized_graph
            self.distances = data.distances_dict
            self.stops_df = data.stops_df
            self.routes_df = data.routes_df
            self.stops_df_by_name = data.stops_df_by_name
            self.stop_times_0 = data.stop_times_0_dict
            self.stop_times_24 = data.stop_times_24_dict
            self.paths = dict()
            self.day_to_services_dict = data.day_to_services_dict
            for node in self.graph.nodes():
                self.paths[node] = dict()


