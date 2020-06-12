from copy import copy
from queue import PriorityQueue

from utils import *
import pandas as pd
from solvers.ISolver import ISolver
from DataClasses.Transfer import Transfer
from DataClasses.TransferQuery import TransferQuery
from DataClasses.MeetingQuery import MeetingQuery
from DataClasses.SequenceQuery import SequenceQuery


class FloydSolver(ISolver):
    def __init__(self, graph_data):
        self.graph = graph_data.graph
        self.distances = graph_data.distances
        self.stop_times_df = graph_data.stop_times_df
        self.stops_df = graph_data.stops_df
        self.routes_df = graph_data.routes_df
        self.stops_df_by_name = graph_data.stops_df_by_name
        self.paths = {}
        for node in self.graph.nodes():
            self.paths[node] = {}

    def find_connections(self, query: TransferQuery):
        current_time = time_to_int(query.start_time)
        current_date = query.start_date
        start_stop_id = self.stops_df_by_name.at[query.start_stop_name, 'stop_id']
        end_stop_id = self.stops_df_by_name.at[query.end_stop_name, 'stop_id']

        paths = self.get_paths(start_stop_id, end_stop_id)
        connections = []

        for path in paths:
            results = self.find_routes(path, current_time)
            if results is not None:

                connection = []
                for transfer in results:
                    index, current_stop_id, next_stop_id, departure_time, arrival_time = transfer
                    route_name = self.routes_df.at[index, 'route_name']
                    current_stop_name = self.stops_df.at[current_stop_id, 'stop_name']
                    next_stop_name = self.stops_df.at[next_stop_id, 'stop_name']
                    start_time = int_to_time(departure_time)
                    start_date = shift_date(current_date, departure_time)
                    end_time = int_to_time(arrival_time)
                    end_date = shift_date(current_date, arrival_time)

                    connection.append(
                        Transfer(route_name, current_stop_name, next_stop_name, start_date, start_time, end_date,
                                 end_time))
                connections.append(connection)
        return connections

    def find_meeting_points(self, query: MeetingQuery):
        start_stop_ids = list(map(lambda x: int(self.stops_df_by_name.at[x, 'stop_id']), query.start_stop_names))
        if query.metric == 'square':
            metric = lambda l: sum(map(lambda i: i * i, l))
        elif query.metric == 'sum':
            metric = lambda l: sum(l)
        elif query.metric == 'max':
            metric = lambda l: max(l)
        else:
            return None
        meeting_metrics = []
        for end_stop_id in self.distances:
            distances_to_destination = list(map(lambda stop_id: self.distances[stop_id][end_stop_id], start_stop_ids))
            meeting_metrics.append((end_stop_id, metric(distances_to_destination)))
        meeting_metrics.sort(key=lambda x: x[1])
        meeting_points = list(map(lambda x: self.stops_df.at[x[0], 'stop_name'], meeting_metrics[0:10]))
        return meeting_points

    def find_optimal_sequence(self, query: SequenceQuery):
        def gen(stop_ids: list, current_stop_id, last_stop_id, sequence: list, weight: int):
            if stop_ids:
                for next_stop_id in stop_ids:
                    next_stop_ids = copy(stop_ids)
                    next_stop_ids.remove(next_stop_id)
                    next_sequence = copy(sequence)
                    next_sequence.append(next_stop_id)
                    next_weight = weight + self.distances[current_stop_id][next_stop_id]
                    yield from gen(next_stop_ids, next_stop_id, last_stop_id, next_sequence, next_weight)
            else:
                sequence.append(last_stop_id)
                weight = weight + self.distances[current_stop_id][last_stop_id]
                yield sequence, weight

        stops_to_visit_ids = list(map(lambda x: int(self.stops_df_by_name.at[x, 'stop_id']), query.stops_to_visit))
        start_stop_id = int(self.stops_df_by_name.at[query.start_stop_name, 'stop_id'])
        end_stop_id = int(self.stops_df_by_name.at[query.end_stop_name, 'stop_id'])
        sequences = list(gen(stops_to_visit_ids, start_stop_id, end_stop_id, [start_stop_id], 0))
        optimal_order = min(sequences, key=lambda x: x[1])
        print(optimal_order[1])
        optimal_order = list(map(lambda x: self.stops_df.at[x, 'stop_name'], optimal_order[0]))
        return optimal_order

    def find_routes(self, path, time):
        # TODO smart join could return paths for all hours at once
        # TODO seek for routes from end_stop
        # TODO change to generatorin the future
        results = []
        for index in range(len(path) - 1):
            current_stop = path[index]
            next_stop = path[index + 1]
            current_stop_times_df = \
                self.stop_times_df[self.stop_times_df['stop_id'] == current_stop].reset_index('stop_sequence')[
                    ['departure_time']]
            next_stop_times_df = \
                self.stop_times_df[self.stop_times_df['stop_id'] == next_stop].reset_index('stop_sequence')[
                    ['departure_time']]
            transfers_df = current_stop_times_df.join(next_stop_times_df, how='inner', lsuffix='_current',
                                                      rsuffix='_next')
            transfers_df = transfers_df[transfers_df.departure_time_current > time]
            transfers_df = transfers_df[transfers_df.departure_time_current < transfers_df.departure_time_next]
            if transfers_df.empty:
                return None

            transfers_df = transfers_df[
                transfers_df.departure_time_current == transfers_df.departure_time_current.min()]
            for index, row in transfers_df.iterrows():
                departure_time = row['departure_time_current']
                arrival_time = row['departure_time_next']
                results.append((index, current_stop, next_stop, departure_time, arrival_time))
                time = arrival_time
                break
        return results

    def get_paths(self, start_node, end_node):
        if start_node == end_node:
            return []
        if end_node not in self.paths[start_node]:
            self.paths[start_node][end_node] = self.calculate_paths(start_node, end_node)
        return self.paths[start_node][end_node]

    def calculate_paths(self, start_node, end_node):
        queue = PriorityQueue()
        count = 0
        paths = []
        costs = []
        routes_dict = []
        queue.put((0, 0, start_node, [start_node], []))
        while queue and count < 20:
            priority, weight, node_id, path, routes = queue.get()
            if node_id == end_node:
                count = count + 1
                paths.append(path)
                costs.append(priority)
                continue
            for neighbor_id in self.graph.neighbors(node_id):
                n_weight = weight + self.graph.edges[node_id, neighbor_id]['weight']
                n_priority = n_weight + self.distances[neighbor_id][end_node]
                n_path = copy(path)
                n_path.append(neighbor_id)
                n_routes = copy(routes)
                route = self.graph.edges[node_id, neighbor_id]['route_ids']
                if self.is_redundant(n_routes, route):
                    continue
                n_routes.append(route)
                if (n_routes, neighbor_id) not in routes_dict:
                    routes_dict.append((n_routes, neighbor_id))
                    queue.put((n_priority, n_weight, neighbor_id, n_path, n_routes))
        return paths

    def is_redundant(self, n_routes, route):
        if not n_routes:
            return False
        index = len(n_routes) - 1
        last_route = n_routes[index]
        if set(last_route).issubset(route) or set(route).issubset(last_route):
            return True
        return False
