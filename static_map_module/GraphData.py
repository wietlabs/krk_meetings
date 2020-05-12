import networkx as nx
import pandas as pd
from dataclasses import dataclass
from static_timetable_module.gtfs_static.Data import Data


@dataclass
class GraphData(Data):  # server has reference to its instance
    graph: nx.Graph
    distances: dict
    stop_times_df: pd.DataFrame
    node_to_hub_df: pd.DataFrame
