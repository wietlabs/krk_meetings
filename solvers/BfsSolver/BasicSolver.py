from pathlib import Path

import pandas as pd
import networkx as nx

from solvers.ISolver import ISolver
from DataClasses.Query import Query
from DataClasses.ParsedData import ParsedData


class BasicSolver(ISolver):
    def __init__(self, parsed_data: ParsedData):
        # self.G = nx.read_gpickle(Path(__file__).parent / 'tmp' / 'G.gpickle')
        # self.G_R = nx.read_gpickle(Path(__file__).parent / 'tmp' / 'G_R.gpickle')
        # self.stops_df = parsed_data.stops_df
        # self.unique_stop_times_df = pd.read_pickle(Path(__file__).parent / 'tmp' / 'unique_stop_times_df.pickle')
        # return

        G = nx.DiGraph()

        stops_df = parsed_data.stops_df
        stop_times_df = parsed_data.stop_times_df
        transfers_df = parsed_data.transfers_df

        transfers_df = transfers_df[['start_time', 'end_time', 'start_stop_id', 'end_stop_id', 'duration']]

        unique_stop_times_df = stop_times_df.reset_index()[['stop_id', 'departure_time']]
        unique_stop_times_df['departure_time'] %= 24 * 60 * 60
        unique_stop_times_df.drop_duplicates(inplace=True)
        unique_stop_times_df.set_index(['stop_id', 'departure_time'], inplace=True)
        unique_stop_times_df.sort_index(inplace=True)
        # TODO: move to extractor?

        G.add_nodes_from(unique_stop_times_df.index)

        G.add_weighted_edges_from(
            ((start_stop_id, start_time), (end_stop_id, end_time), duration)
            for _, start_time, end_time, start_stop_id, end_stop_id, duration in transfers_df.itertuples()
        )
        # TODO: include weekdays using service_id

        # trick #1: add destination nodes
        G.add_nodes_from(
            (stop_id, None)
            for stop_id in stops_df.index
        )

        # trick #2: merged waiting edges
        G.add_weighted_edges_from(
            ((stop_id, start_time), (stop_id, end_time), (end_time - start_time) % (24 * 60 * 60))
            for stop_id, df in unique_stop_times_df.groupby('stop_id')
            for (_, start_time), (_, end_time) in nx.utils.pairwise(df.index, cyclic=True)
        )

        # trick #3: use reversed graph to find the latest departure time
        G_R = G.reverse()

        G.add_edges_from((
            ((stop_id, time), (stop_id, None))
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        G_R.add_edges_from((
            ((stop_id, time), (stop_id, None))
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        nx.write_gpickle(G, Path(__file__).parent / 'tmp' / 'G.gpickle')
        nx.write_gpickle(G_R, Path(__file__).parent / 'tmp' / 'G_R.gpickle')
        unique_stop_times_df.to_pickle(Path(__file__).parent / 'tmp' / 'unique_stop_times_df.pickle')

        self.G = G
        self.G_R = G_R
        self.stops_df = parsed_data.stops_df
        self.unique_stop_times_df = unique_stop_times_df

    def find_connection(self, query: Query):
        start_time = query.start_time
        start_stop_id = query.start_stop_id
        end_stop_id = query.end_stop_id

        unique_stop_times = self.unique_stop_times_df.xs(start_stop_id).index
        idx = unique_stop_times.searchsorted(start_time)
        if idx == len(unique_stop_times):
            idx = 0
        start_time = unique_stop_times[idx]

        source = (start_stop_id, start_time)
        target = (end_stop_id, None)

        # shortest_path = nx.shortest_path(self.G, source, target)
        # path = shortest_path[:-1]

        shortest_path_length = nx.shortest_path_length(self.G, source, target, 'weight')
        end_time = (start_time + shortest_path_length) % (24 * 60 * 60)

        source = (end_stop_id, end_time)
        target = (start_stop_id, None)

        shortest_inverted_path = nx.shortest_path(self.G_R, source, target, 'weight')
        path = shortest_inverted_path[:-1][::-1]

        result_df = pd.DataFrame(path, columns=['stop_id', 'time'])
        return result_df
