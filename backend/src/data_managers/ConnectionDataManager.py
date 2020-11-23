import networkx as nx
import pandas as pd
import time
from src.data_managers.DataManager import DataManager
from src.utils import load_pickle
from src.exchanges import EXCHANGES, MESSAGES


class ConnectionDataManager(DataManager):
    def __init__(self, data_path):
        super().__init__()
        self.data_path = data_path
        self.last_delay_update = time.time()

    @property
    def exchange(self):
        return EXCHANGES.CONNECTION_DATA_MANAGER.value

    def handle_message(self, msg):
        if msg == MESSAGES.DATA_UPDATED.value:
            self.update_data()

    def get_data(self):
        data = dict()
        data["averge_graph"] = nx.read_gpickle(self.data_path.averge_graph.value)
        data["kernelized_graph"] = nx.read_gpickle(self.data_path.kernelized_graph.value)
        data["distances"] = load_pickle(self.data_path.distances.value)
        data["stops_df"] = pd.read_pickle(self.data_path.stops_df.value)
        data["routes_df"] = pd.read_pickle(self.data_path.routes_df.value)
        data["stops_df_by_name"] = pd.read_pickle(self.data_path.stops_df_by_name.value)
        data["stop_times_0"] = load_pickle(self.data_path.stop_times_0_dict.value)
        data["stop_times_24"] = load_pickle(self.data_path.stop_times_24_dict.value)
        data["day_to_services_dict"] = load_pickle(self.data_path.day_to_services_dict.value)
        data["adjacent_stops"] = load_pickle(self.data_path.adjacent_stops.value)
        data["routes_to_stops_dict"] = load_pickle(self.data_path.routes_to_stops_dict.value)
        data["exception_days_dict"] = load_pickle(self.data_path.exception_days.value)
        return data
