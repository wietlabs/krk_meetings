import networkx as nx
import pandas as pd
import time
from src.data_managers.DataManager import DataManager
from src.utils import load_pickle
from src.config import FloydDataPaths
from src.exchanges import EXCHANGES, MESSAGES


class ConnectionDataManager(DataManager):
    def __init__(self):
        super().__init__()
        self.last_delay_update = time.time()

    @property
    def exchange(self):
        return EXCHANGES.CONNECTION_DATA_MANAGER.value

    def handle_message(self, msg):
        if msg == MESSAGES.DATA_UPDATED.value:
            self.update_data()

    def get_data(self):
        data = dict()
        data["graph"] = nx.read_gpickle(FloydDataPaths.floyd_graph.value)
        data["kernelized_graph"] = nx.read_gpickle(FloydDataPaths.kernelized_floyd_graph.value)
        data["distances"] = load_pickle(FloydDataPaths.distances.value)
        data["stops_df"] = pd.read_pickle(FloydDataPaths.stops_df.value)
        data["routes_df"] = pd.read_pickle(FloydDataPaths.routes_df.value)
        data["stops_df_by_name"] = pd.read_pickle(FloydDataPaths.stops_df_by_name.value)
        data["stop_times_0"] = load_pickle(FloydDataPaths.stop_times_0_dict.value)
        data["stop_times_24"] = load_pickle(FloydDataPaths.stop_times_24_dict.value)
        data["day_to_services_dict"] = load_pickle(FloydDataPaths.day_to_services_dict.value)
        data["adjacent_stops"] = load_pickle(FloydDataPaths.adjacent_stops.value)
        data["routes_to_stops_dict"] = load_pickle(FloydDataPaths.routes_to_stops_dict.value)
        data["exception_days_dict"] = load_pickle(FloydDataPaths.exception_days.value)
        return data
