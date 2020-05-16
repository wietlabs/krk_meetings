import networkx as nx
import pandas as pd
from dataclasses import dataclass
from DataClasses.Data import Data


@dataclass
class GraphData(Data):  # server has reference to its instance
    graph: nx.Graph
    distances: dict
    stop_times_df: pd.DataFrame
    stops_df: pd.DataFrame
