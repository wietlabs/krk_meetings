import networkx as nx
import pandas as pd
import time

from krk_meetings.config import FloydDataPaths
from krk_meetings.data_managers.DataManager import DataManager
from krk_meetings.utils import load_pickle
from krk_meetings.exchanges import EXCHANGES, MESSAGES


class ConnectionDataManager(DataManager):
    def __init__(self, data_path):
        super().__init__()
        self.data_path = data_path
        self.delays_df = None
        self.last_delay_update = time.time()

    @property
    def exchange(self):
        return EXCHANGES.CONNECTION_DATA_MANAGER.value

    def handle_message(self, msg):
        if msg == MESSAGES.DATA_UPDATED.value:
            self.update_data()
        elif msg == MESSAGES.DELAYS_UPDATED.value:
            self.update_delays_df()

    def get_data(self):
        data = dict()
        data["graph"] = nx.read_gpickle(self.data_path.floyd_graph.value)
        data["kernelized_graph"] = nx.read_gpickle(self.data_path.kernelized_floyd_graph.value)
        data["distances"] = load_pickle(self.data_path.distances.value)
        data["stops_df"] = pd.read_pickle(self.data_path.stops_df.value)
        data["routes_df"] = pd.read_pickle(self.data_path.routes_df.value)
        data["stops_df_by_name"] = pd.read_pickle(self.data_path.stops_df_by_name.value)
        data["current_stop_times"] = load_pickle(self.data_path.current_stop_times_dict.value)
        data["next_stop_times"] = load_pickle(self.data_path.next_stop_times_dict.value)
        data["previous_stop_times"] = load_pickle(self.data_path.previous_stop_times_dict.value)
        data["day_to_services_dict"] = load_pickle(self.data_path.day_to_services_dict.value)
        data["adjacent_stops"] = load_pickle(self.data_path.adjacent_stops.value)
        data["routes_to_stops_dict"] = load_pickle(self.data_path.routes_to_stops_dict.value)
        data["exception_days_dict"] = load_pickle(self.data_path.exception_days.value)
        return data

    def update_delays_df(self):
        with self.lock:
            self.delays_df = load_pickle(self.data_path.delays_df.value)
            self.last_delay_update = time.time()

    def get_delays_df(self):
        with self.lock:
            return self.delays_df
