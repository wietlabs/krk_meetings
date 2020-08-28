from math import cos, radians

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from src.data_classes.ParsedData import ParsedData


class Visualization:
    def __init__(self, fix_scaling: bool = True):
        if fix_scaling:
            import sys
            if sys.platform == 'win32':
                import ctypes
                PROCESS_SYSTEM_DPI_AWARE = 1
                ctypes.OleDLL('shcore').SetProcessDpiAwareness(PROCESS_SYSTEM_DPI_AWARE)

        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.fig.tight_layout()
        self.ax.set_aspect(1 / cos(radians(50)))

    def draw_stops(self, parsed_data: ParsedData, draw_transfers: bool = True, **kwargs) -> None:
        stops_df = parsed_data.stops_df

        edges_df = parsed_data.transfers_df[['start_stop_id', 'end_stop_id']].drop_duplicates()

        G = nx.Graph()  # or DiGraph
        G.add_nodes_from(stops_df.index)
        if draw_transfers:
            G.add_edges_from(edges_df.itertuples(index=False))

        pos = {
            stop_id: (stop_lon, stop_lat)
            for stop_id, stop_lat, stop_lon in stops_df[['stop_lat', 'stop_lon']].itertuples()
        }
        params = {'node_size': 4, 'width': 1, **kwargs}
        nx.draw(G, pos, self.ax, **params)

    def draw_result_path(self, result: pd.DataFrame, **kwargs) -> None:
        params = {'color': 'red', 'linewidth': 2, **kwargs}
        self.ax.plot(result['stop_lon'], result['stop_lat'], **params)

    def savefig(self, path: str) -> None:
        self.fig.savefig(path)

    def show(self) -> None:
        self.fig.show()
