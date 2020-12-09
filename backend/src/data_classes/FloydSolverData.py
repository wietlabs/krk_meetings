import json

import networkx as nx
import pandas as pd
from dataclasses import dataclass
from src.data_classes.Data import Data
from networkx.readwrite import json_graph


@dataclass
class FloydSolverData(Data):  # broker has reference to its instance
    graph: nx.DiGraph
    kernelized_graph: nx.DiGraph
    distances_dict: dict
    day_to_services_dict: dict
    stop_times_0_dict: dict
    stop_times_24_dict: dict
    routes_to_stops_dict: dict
    adjacent_stops: dict
    stops_df: pd.DataFrame
    routes_df: pd.DataFrame
    stops_df_by_name: pd.DataFrame
