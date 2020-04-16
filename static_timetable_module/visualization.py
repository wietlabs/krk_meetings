import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from math import cos, radians

if __name__ == '__main__':
    stops_df = pd.read_pickle('tmp/stops_df.pkl')
    avg_durations_df = pd.read_pickle('tmp/avg_durations_df.pkl')

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
