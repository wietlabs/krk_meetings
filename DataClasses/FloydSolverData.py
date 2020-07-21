import networkx as nx
import pandas as pd
from dataclasses import dataclass
from DataClasses.Data import Data


@dataclass
class FloydSolverData(Data):  # server has reference to its instance
    graph: nx.DiGraph
    kernelized_graph: nx.DiGraph
    distances_dict: dict
    day_to_services_dict: dict
    stop_times_0_dict: dict
    stop_times_24_dict: dict
    stops_df: pd.DataFrame
    routes_df: pd.DataFrame
    stops_df_by_name: pd.DataFrame
