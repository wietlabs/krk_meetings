from datetime import timedelta
from typing import List

import networkx as nx

from src.alternative_solvers.BfsSolverData import BfsSolverData
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_classes.Connection import Connection
from src.data_classes.Transfer import Transfer
from src.solver.IConnectionSolver import IConnectionSolver


class BfsConnectionSolver(IConnectionSolver):
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

    def find_connections(self, query: ConnectionQuery) -> List[Connection]:
        MINUTE = 60
        HOUR = 60 * MINUTE
        DAY = 24 * HOUR
        WEEK = 7 * DAY

        start_time = query.start_datetime.weekday() * DAY \
                     + query.start_datetime.hour * HOUR \
                     + query.start_datetime.minute * MINUTE \
                     + query.start_datetime.second
        base_datetime = query.start_datetime - timedelta(seconds=start_time)

        start_stop_id = query.start_stop_id
        end_stop_id = query.end_stop_id

        # step 1: find next earliest possible departure time
        unique_departure_times = self.data.unique_departure_times_df.xs(start_stop_id).index
        idx = unique_departure_times.searchsorted(start_time)
        if idx == len(unique_departure_times):
            idx = 0
        start_time = unique_departure_times[idx]
        end_time = None

        if self.earliest_arrival_time:
            # step 2: calculate the earliest arrival time by finding the shortest path length
            source = (start_stop_id, start_time)
            target = (end_stop_id, None)
            shortest_path_length = nx.shortest_path_length(self.data.G, source, target, 'weight')
            end_time = (start_time + shortest_path_length) % WEEK

            if self.latest_departure_time:
                # step 3: calculate the latest departure time by finding the shortest path length in the reversed graph
                source = (end_stop_id, end_time)
                target = (start_stop_id, None)
                shortest_path_length = nx.shortest_path_length(self.data.G_R, source, target, 'weight')
                start_time = (end_time - shortest_path_length) % WEEK

        # step 4: find sequence of transfers
        source = (start_stop_id, start_time, None, None, None)
        target = (end_stop_id, end_time, None, None, None)
        shortest_path = nx.shortest_path(self.data.G_T, source, target, 'weight')

        # step 5: reconstruct the result
        changes = []
        previous_trip = None
        for node in shortest_path:
            current_trip = node[2:]
            if current_trip != previous_trip:
                previous_trip = current_trip
                changes.append(node)

        def transfers_gen():
            for (start_stop_id, start_time, block_id, trip_num, service_id), (end_stop_id, end_time, _, _, _) in zip(changes[1::2], changes[2::2]):
                route_id = self.data.trips_df.at[(service_id, block_id, trip_num), 'route_id']
                start_datetime = base_datetime + timedelta(seconds=start_time)
                end_datetime = base_datetime + timedelta(seconds=end_time)
                yield Transfer(route_id, start_stop_id, end_stop_id, start_datetime, end_datetime)

        transfers = list(transfers_gen())
        connection = Connection(transfers)
        results = [connection]
        return results
