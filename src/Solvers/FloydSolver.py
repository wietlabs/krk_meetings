from copy import copy
from queue import PriorityQueue
from typing import List
from src.DataClasses.Connection import Connection
from src.utils import *
from src.Solvers.ISolver import ISolver
from src.DataClasses.Transfer import Transfer
from src.DataClasses.TransferQuery import TransferQuery
from src.DataClasses.MeetingQuery import MeetingQuery
from src.DataClasses.SequenceQuery import SequenceQuery
from src.config import SEARCHING_TIME, MAX_PRIORITY_MULTIPLIER


class FloydSolver(ISolver):
    def __init__(self, graph_data):
        self.graph = graph_data.graph
        self.distances = graph_data.distances
        self.stops_df = graph_data.stops_df
        self.routes_df = graph_data.routes_df
        self.stops_df_by_name = graph_data.stops_df_by_name
        self.stop_times = dict()
        self.paths = dict()
        for node in self.graph.nodes():
            self.paths[node] = dict()

        stop_ids = self.stops_df.index.tolist()
        self.stop_times_df = graph_data.stop_times_df
        for stop_id in stop_ids:
            self.stop_times[stop_id] = graph_data.stop_times_df[graph_data.stop_times_df['stop_id'] == stop_id] \
                .reset_index('stop_sequence')[['departure_time']]


    def find_connections(self, query: TransferQuery) -> List[Connection]:
        current_time = time_to_int(query.start_time)
        current_date = query.start_date
        start_stop_id = self.stops_df_by_name.at[query.start_stop_name, 'stop_id']
        end_stop_id = self.stops_df_by_name.at[query.end_stop_name, 'stop_id']

        paths = self.get_paths(start_stop_id, end_stop_id)
        connections = []
        for path in paths:
            results = self.find_routes(path, current_time)
            if results is not None:
                for result in results:
                    transfers = []
                    for transfer in result:
                        index, current_stop_id, next_stop_id, departure_time, arrival_time = transfer
                        route_name = self.routes_df.at[index, 'route_name']
                        current_stop_name = self.stops_df.at[current_stop_id, 'stop_name']
                        next_stop_name = self.stops_df.at[next_stop_id, 'stop_name']
                        start_time = int_to_time(departure_time)
                        start_date = shift_date(current_date, departure_time)
                        end_time = int_to_time(arrival_time)
                        end_date = shift_date(current_date, arrival_time)

                        transfers.append(
                            Transfer(route_name, current_stop_name, next_stop_name, start_date, start_time, end_date,
                                     end_time))

                        connection = Connection(transfers)
                        connections.append(connection)
        connections.sort(key=lambda x: x.transfers[0].start_time)
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
        optimal_order = list(map(lambda x: self.stops_df.at[x, 'stop_name'], optimal_order[0]))
        return optimal_order

    def find_routes(self, path, time):
        # TODO smart join could return paths for all hours at once
        # TODO seek for routes from end_stop
        # TODO change to generatorin the future
        results = []
        results_df_not_exists = True
        for i in range(len(path) - 1):
            current_stop = path[i]
            next_stop = path[i + 1]

            cst_df = self.stop_times[current_stop]
            nst_df = self.stop_times[next_stop]

            cst_df = cst_df[time <= cst_df.departure_time]
            cst_df = cst_df[cst_df.departure_time <= time + SEARCHING_TIME]
            nst_df = nst_df[time <= nst_df.departure_time]
            nst_df = nst_df[nst_df.departure_time <= time + SEARCHING_TIME]

            transfers_df = cst_df.join(nst_df, how='inner', lsuffix='_c', rsuffix='_n')
            transfers_df = transfers_df[transfers_df.departure_time_c < transfers_df.departure_time_n]
            transfers_df['index'] = transfers_df.index

            if results_df_not_exists:
                results_df_not_exists = False
                results_df = transfers_df
                results_df.columns = [str(col) + '0' for col in results_df.columns]
                results_df = results_df.sort_values(by=['departure_time_n0'])
                results_df = results_df.drop_duplicates(subset='departure_time_c0', keep='first')
            else:
                results_df = results_df.assign(c=1)
                results_df = results_df.merge(transfers_df.assign(c=1))
                results_df = results_df.drop('c', 1)
                results_df.rename(columns={'departure_time_c': 'departure_time_c' + str(i),
                                           'departure_time_n': 'departure_time_n' + str(i),
                                           'index': 'index' + str(i)},
                                  inplace=True)
                results_df = results_df[results_df['departure_time_n' + str(i - 1)] < results_df['departure_time_c' + str(i)]]
                results_df = results_df.sort_values(by=['departure_time_n' + str(i)])
                results_df = results_df.drop_duplicates(subset='departure_time_c0', keep='first')
        for index, row in results_df.iterrows():
            result = []
            for i in range(len(path) - 1):
                index = row['index' + str(i)]
                departure_time = row['departure_time_c' + str(i)]
                arrival_time = row['departure_time_n' + str(i)]
                result.append((index, path[i], path[i+1], departure_time, arrival_time))
            results.append(result)
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
        routes_to_node = {}
        queue.put((0, 0, start_node, [start_node], []))
        max_priority = self.distances[start_node][end_node] * MAX_PRIORITY_MULTIPLIER
        priority = 0
        while queue and priority < max_priority:
            priority, weight, node_id, path, routes = queue.get()
            subset_route = False
            current_route_set = set()
            for route in routes:
                current_route_set.update(set(route))
            if node_id in routes_to_node:
                for route_to_node in routes_to_node[node_id]:
                    if route_to_node.issubset(current_route_set):
                        subset_route = True
                        break
                if subset_route:
                    continue
            else:
                routes_to_node[node_id] = []
            routes_to_node[node_id].append(current_route_set)

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
