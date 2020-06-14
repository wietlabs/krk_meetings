from typing import List, Tuple, Optional

import networkx as nx

from DataClasses.Connection import Connection
from DataClasses.Transfer import Transfer
from solvers.BfsSolver.BfsSolverData import BfsSolverData
from solvers.ISolver import ISolver
from DataClasses.TransferQuery import TransferQuery
from utils import int_to_time


class BfsSolver(ISolver):
    def __init__(self, data: BfsSolverData, *,
                 earliest_arrival_time: bool = True,
                 latest_departure_time: bool = True,
                 minimal_transfers_count: bool = True):
        if latest_departure_time and not earliest_arrival_time:
            raise ValueError()

        if not minimal_transfers_count:
            raise NotImplementedError()

        self.data = data
        self.earliest_arrival_time = earliest_arrival_time
        self.latest_departure_time = latest_departure_time
        self.minimal_transfers_count = minimal_transfers_count

    def find_connections(self, query: TransferQuery) -> List[Connection]:
        # TODO: handle start_date
        start_time = query.start_time.hour * 3600 + query.start_time.minute * 60 + query.start_time.second
        start_stop_id = int(self.data.stops_df_by_name.at[query.start_stop_name, 'stop_id'])
        end_stop_id = int(self.data.stops_df_by_name.at[query.end_stop_name, 'stop_id'])

        # step 1: find next earliest possible departure time
        unique_stop_times = self.data.unique_stop_times_df.xs(start_stop_id).index
        idx = unique_stop_times.searchsorted(start_time)
        if idx == len(unique_stop_times):
            idx = 0
        start_time = unique_stop_times[idx]
        end_time = None

        if self.earliest_arrival_time:
            # step 2: calculate the earliest arrival time by finding the shortest path length
            source = (start_stop_id, start_time)
            target = (end_stop_id, None)
            shortest_path_length = nx.shortest_path_length(self.data.G, source, target, 'weight')
            end_time = (start_time + shortest_path_length) % (24 * 60 * 60)

            if self.latest_departure_time:
                # step 3: calculate the latest departure time by finding the shortest path length in the reversed graph
                source = (end_stop_id, end_time)
                target = (start_stop_id, None)
                shortest_path_length = nx.shortest_path_length(self.data.G_R, source, target, 'weight')
                start_time = (end_time - shortest_path_length) % (24 * 60 * 60)

        # step 4: find sequence of transfers
        source = (start_stop_id, start_time, None, None, None)
        target = (end_stop_id, end_time, None, None, None)
        shortest_path = nx.shortest_path(self.data.G_T, source, target, 'weight')

        # step 5: reconstruct the result
        changes = []
        last_trip = False
        for node in shortest_path:
            current_trip = node[2:]
            if current_trip != last_trip:
                last_trip = current_trip
                changes.append(node)

        transfers = []
        for (start_stop_id, start_time, block_id, trip_num, service_id), (end_stop_id, end_time, _, _, _) in zip(changes[1::2], changes[2::2]):
            route_id = self.data.trips_df.at[(service_id, block_id, trip_num), 'route_id']
            route_number = self.data.routes_df.at[route_id, 'route_short_name']
            start_stop_name = self.data.stops_df.at[start_stop_id, 'stop_name']
            end_stop_name = self.data.stops_df.at[end_stop_id, 'stop_name']
            start_date = end_date = query.start_date  # TODO: retrieve start and end date
            start_time = int_to_time(start_time)
            end_time = int_to_time(end_time)
            transfer = Transfer(route_number, start_stop_name, end_stop_name, start_date, start_time, end_date, end_time)
            transfers.append(transfer)

        connection = Connection(transfers)

        results = [connection]
        return results
