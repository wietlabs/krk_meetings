import pandas as pd
import networkx as nx
from dataclasses import dataclass
from static_timetable_module.gtfs_static.Data import Data


@dataclass
class ExtractedMap(Data):  # server has reference to its instance
    graph: nx.MultiDiGraph
    kernelized_graph: nx.MultiDiGraph
    distances: dict
    #paths: dict
