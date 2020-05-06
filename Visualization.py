import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from math import cos, radians
from pathlib import Path

from static_timetable_module.gtfs_static.ExtractedData import ExtractedData

class Visualization:
    def __init__(self, fix_scaling=True):
        if fix_scaling:
            import sys
            if sys.platform == 'win32':
                import ctypes
                PROCESS_SYSTEM_DPI_AWARE = 1
                ctypes.OleDLL('shcore').SetProcessDpiAwareness(PROCESS_SYSTEM_DPI_AWARE)

        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.ax.set_aspect(aspect=1 / cos(radians(50)))
        self.fig.tight_layout()

    def draw_stops(self, extracted_data: ExtractedData, draw_transfers=True, **kwargs) -> None:
        stops_df = extracted_data.stops_df
        avg_durations_df = extracted_data.avg_durations_df

        G = nx.Graph()  # or DiGraph
        G.add_nodes_from(stops_df.index)
        if draw_transfers:
            G.add_edges_from(avg_durations_df.index)

        pos = dict(stops_df[['stop_lon', 'stop_lat']].iterrows())

        params = {'node_size': 4, 'edge_width': 2, **kwargs}
        nx.draw(G, pos, self.ax, **params)

    def draw_result_path(self, result: pd.DataFrame, **kwargs) -> None:
        params = {'color': 'red', 'linewidth': 2, **kwargs}
        self.ax.plot(result['stop_lon'], result['stop_lat'], **params)

    def savefig(self, path: str) -> None:
        self.fig.savefig(path)

    def show(self) -> None:
        plt.show()


if __name__ == '__main__':
    path = Path(__file__).parent / 'static_timetable_module' / 'gtfs_static' / 'tmp' / 'extracted_data.pickle'
    extracted_data = ExtractedData.load(path)

    visualization = Visualization()
    visualization.draw_stops(extracted_data)
    visualization.show()
