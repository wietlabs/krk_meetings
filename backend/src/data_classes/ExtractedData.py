from dataclasses import dataclass

import networkx as nx
import pandas as pd

from src.config import FloydDataPaths
from src.data_classes.Data import Data
from src.utils import save_pickle


@dataclass
class ExtractedData(Data):
    floyd_graph: nx.DiGraph
    kernelized_floyd_graph: nx.DiGraph
    distances: dict
    day_to_services_dict: dict
    current_stop_times_dict: dict
    previous_stop_times_dict: dict
    next_stop_times_dict: dict
    routes_to_stops_dict: dict
    adjacent_stops: dict
    exception_days: dict
    stops_df: pd.DataFrame
    routes_df: pd.DataFrame
    stops_df_by_name: pd.DataFrame
    stop_times_df: pd.DataFrame

    def save(self, data_paths=FloydDataPaths):
        nx.write_gpickle(self.floyd_graph, data_paths.floyd_graph.value)
        nx.write_gpickle(self.kernelized_floyd_graph, data_paths.kernelized_floyd_graph.value)
        save_pickle(self.distances, data_paths.distances.value)
        save_pickle(self.day_to_services_dict, data_paths.day_to_services_dict.value)
        save_pickle(self.current_stop_times_dict, data_paths.current_stop_times_dict.value)
        save_pickle(self.previous_stop_times_dict, data_paths.previous_stop_times_dict.value)
        save_pickle(self.next_stop_times_dict, data_paths.next_stop_times_dict.value)
        save_pickle(self.routes_to_stops_dict, data_paths.routes_to_stops_dict.value)
        save_pickle(self.adjacent_stops, data_paths.adjacent_stops.value)
        save_pickle(self.exception_days, data_paths.exception_days.value)
        self.stops_df.to_pickle(data_paths.stops_df.value)
        self.routes_df.to_pickle(data_paths.routes_df.value)
        self.stops_df_by_name.to_pickle(data_paths.stops_df_by_name.value)
        self.stop_times_df.to_pickle(data_paths.stops_times_df.value)
