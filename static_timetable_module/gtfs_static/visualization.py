import networkx as nx
import matplotlib.pyplot as plt
from math import cos, radians
from pathlib import Path
from static_timetable_module.gtfs_static.ExtractedData import ExtractedData

if __name__ == '__main__':
    path = Path(__file__).parent / 'tmp' / 'extracted_data.pickle'
    extracted_data = ExtractedData.load(path)

    stops_df = extracted_data.stops_df
    avg_durations_df = extracted_data.avg_durations_df

    G = nx.Graph()  # or DiGraph
    G.add_nodes_from(stops_df.index)
    G.add_edges_from(avg_durations_df.index)

    pos = dict(stops_df[['stop_lon', 'stop_lat']].iterrows())

    fig, ax = plt.subplots()
    ax.set_aspect(aspect=1/cos(radians(50)))
    nx.draw(G, pos, ax, node_size=8, width=2)

    fig.tight_layout()

    # fig.savefig('map.svg')
    plt.show()
