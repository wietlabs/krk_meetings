from dataclasses import dataclass

import pandas as pd
import networkx as nx

from DataClasses.Data import Data


@dataclass
class BfsSolverData(Data):
    G: nx.DiGraph
    G_R: nx.DiGraph
    G_T: nx.DiGraph
    stops_df: pd.DataFrame
    stops_df_by_name: pd.DataFrame
    unique_stop_times_df: pd.DataFrame
    trips_df: pd.DataFrame
    routes_df: pd.DataFrame
