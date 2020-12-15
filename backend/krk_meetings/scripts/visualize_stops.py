import pickle
from math import cos, radians
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from krk_meetings.data_provider.gtfs_static.Corrector import Corrector
from krk_meetings.data_provider.gtfs_static.Merger import Merger
from krk_meetings.data_provider.gtfs_static.Parser import Parser

if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent / 'data_provider' / 'data'

    parser = Parser()
    parsed_data_A = parser.parse(data_dir / 'GTFS_KRK_A.zip')
    parsed_data_T = parser.parse(data_dir / 'GTFS_KRK_T.zip')

    merger = Merger()
    merged_data, _ = merger.merge(parsed_data_A, parsed_data_T)

    corrector = Corrector()
    corrected_data = corrector.correct(merged_data)

    with open(data_dir / 'border.pickle', 'rb') as f:
        border = pickle.load(f)

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.tight_layout()
    ax.set_aspect(1 / cos(radians(50)))

    stops_df = merged_data.stops_df
    edges_df = merged_data.transfers_df[['start_stop_id', 'end_stop_id']].drop_duplicates()

    G = nx.Graph()
    G.add_nodes_from(stops_df.index)
    G.add_edges_from(edges_df.itertuples(index=False))

    pos = {
        stop_id: (stop_lon, stop_lat)
        for stop_id, stop_lat, stop_lon in stops_df[['stop_lat', 'stop_lon']].itertuples()
    }
    lats, lons = zip(*border)

    plt.fill(lons, lats, color='lightgray', zorder=0)
    nx.draw(G, pos, ax, node_size=2, node_color='black', width=1, edge_color='gray')

    fig.savefig('map.pdf')
