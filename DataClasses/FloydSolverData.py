import networkx as nx
import pandas as pd
from dataclasses import dataclass
from DataClasses.Data import Data


@dataclass
class FloydSolverData(Data):  # server has reference to its instance
    graph: nx.DiGraph
    kernelized_floyd_graph: nx.DiGraph
    distances: dict
    stop_times_df: pd.DataFrame
    stops_df: pd.DataFrame
    routes_df: pd.DataFrame
    stops_df_by_name: pd.DataFrame
