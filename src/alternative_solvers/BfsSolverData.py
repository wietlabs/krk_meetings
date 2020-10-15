from dataclasses import dataclass

import networkx as nx
import pandas as pd

from src.data_classes.Data import Data


@dataclass
class BfsSolverData(Data):
    G: nx.DiGraph
    G_R: nx.DiGraph
    G_T: nx.DiGraph
    unique_stop_times_df: pd.DataFrame
    trips_df: pd.DataFrame
