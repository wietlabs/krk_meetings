from typing import List

import networkx as nx

from DataClasses.Transfer import Transfer
from solvers.BfsSolver.BfsSolverData import BfsSolverData
from solvers.ISolver import ISolver
from DataClasses.TransferQuery import TransferQuery


class BfsSolver(ISolver):
    def __init__(self, data: BfsSolverData):
        self.data = data

    def find_connections(self, query: TransferQuery) -> List[List[Transfer]]:
        # TODO: handle start_date
        start_time = query.start_time.hour * 3600 + query.start_time.minute * 60 + query.start_time.second
        start_stop_id = int(self.data.stops_df_by_name.loc[query.start_stop_name]['stop_id'])
        end_stop_id = int(self.data.stops_df_by_name.loc[query.end_stop_name]['stop_id'])

        # step 1: find next earliest possible departure time
        unique_stop_times = self.data.unique_stop_times_df.xs(start_stop_id).index
        idx = unique_stop_times.searchsorted(start_time)
        if idx == len(unique_stop_times):
            idx = 0
        start_time = unique_stop_times[idx]

        # shortest_path = nx.shortest_path(self.G, source, target)
        # path = shortest_path[:-1]

        # step 2: calculate the earliest arrival time by finding the shortest path length
        source = (start_stop_id, start_time)
        target = (end_stop_id, None)
        shortest_path_length = nx.shortest_path_length(self.data.G, source, target, 'weight')
        end_time = (start_time + shortest_path_length) % (24 * 60 * 60)

        # step 3: calculate the latest departure time by finding the shortest path length in the reversed graph
        source = (end_stop_id, end_time)
        target = (start_stop_id, None)
        shortest_path_length = nx.shortest_path_length(self.data.G_R, source, target, 'weight')
        start_time = (end_time - shortest_path_length) % (24 * 60 * 60)

        # step 4: find sequence of transfers
        source = (start_stop_id, start_time, None)
        target = (end_stop_id, end_time, None)
        shortest_path = nx.shortest_path(self.data.G_B, source, target, 'weight')

        # step 5: reconstruct the result
        sequence = []
        for node in shortest_path:
            print(node)

        results = [sequence]
        return results
