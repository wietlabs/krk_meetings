from copy import copy
from queue import PriorityQueue
from typing import List
from itertools import chain
import pandas as pd

from src.data_classes.ConnectionResults import ConnectionResults
from src.solver.DataManager import DataManager
from src.utils import *
from src.solver.IConnectionSolver import IConnectionSolver
from src.data_classes.Transfer import Transfer
from src.data_classes.ConnectionQuery import ConnectionQuery

from src.config import FLOYD_SOLVER_SEARCHING_TIME, FLOYD_SOLVER_MAX_PRIORITY_MULTIPLIER, FLOYD_SOLVER_MAX_PATHS, \
    WALKING_ROUTE_ID


class ConnectionSolver(IConnectionSolver):
    def __init__(self, ):
        self.data_manager = DataManager()
        self.graph = None
        self.kernelized_graph = None
        self.distances = None
        self.stops_df = None
        self.routes_df = None
        self.stops_df_by_name = None
        self.stop_times_0 = None
        self.stop_times_24 = None
        self.paths = None
        self.day_to_services_dict = None
        self.adjacent_stops = None

        self.data_manager.start()
        self.data_manager.update_data()
        self.update_data()

    def update_data(self):
        if not self.data_manager.up_to_date:
            data = self.data_manager.get_updated_data()
            self.graph = data.graph
            self.kernelized_graph = data.kernelized_graph
            self.distances = data.distances_dict
            self.stops_df = data.stops_df
            self.routes_df = data.routes_df
            self.stops_df_by_name = data.stops_df_by_name
            self.stop_times_0 = data.stop_times_0_dict
            self.stop_times_24 = data.stop_times_24_dict
            self.day_to_services_dict = data.day_to_services_dict
            self.adjacent_stops = data.adjacent_stops
            self.paths = dict()
            for node in self.graph.nodes():
                self.paths[node] = dict()

    def find_connections(self, query: ConnectionQuery) -> List[ConnectionResults]:
        self.update_data()

        current_time = time_to_int(query.start_time)
        current_date = query.start_date
        start_stop_id = query.start_stop_id
        end_stop_id = query.end_stop_id

        paths = self.get_paths(start_stop_id, end_stop_id)
        connections = []
        for path in paths:
            results = self.find_routes(path, current_time, current_date)
            if results is not None:
                for result in results:
                    transfers = []
                    for transfer in result:
                        route_id, current_stop_id, next_stop_id, departure_time, arrival_time = transfer
                        start_time = int_to_time(departure_time)
                        start_date = shift_date(current_date, departure_time)
                        end_time = int_to_time(arrival_time)
                        end_date = shift_date(current_date, arrival_time)

                        transfers.append(
                            Transfer(route_id, current_stop_id, next_stop_id, start_date, start_time, end_date,
                                     end_time))

                    connection = ConnectionResults(transfers)
                    connections.append(connection)
            connections.sort(key=lambda c: c.transfers[0].start_time)
        return connections

    def find_routes(self, path: List[int], start_time: int, start_date: date):
        # TODO smart join could return paths for all hours at once
        # TODO seek for routes from end_stop
        # TODO change to generatorin the future
        day = start_date.weekday()
        current_services = self.day_to_services_dict[day]
        next_services = self.day_to_services_dict[(day + 1) % 7]

        results = []
        results_df = pd.DataFrame()
        for i in range(len(path) - 1):
            current_stop = path[i]
            next_stop = path[i + 1]

            cst_df = pd.concat(chain([self.stop_times_0[next_stop][service] for service in current_services],
                                     [self.stop_times_24[next_stop][service] for service in next_services]))
            nst_df = pd.concat(chain([self.stop_times_0[current_stop][service] for service in current_services],
                                     [self.stop_times_24[current_stop][service] for service in next_services]))

            cst_df = cst_df[start_time <= cst_df.departure_time]
            cst_df = cst_df[cst_df.departure_time <= start_time + FLOYD_SOLVER_SEARCHING_TIME]
            nst_df = nst_df[start_time <= nst_df.departure_time]
            nst_df = nst_df[nst_df.departure_time <= start_time + FLOYD_SOLVER_SEARCHING_TIME]

            transfers_df = cst_df.join(nst_df, how='inner', lsuffix='_c', rsuffix='_n')
            transfers_df = transfers_df[transfers_df.departure_time_c < transfers_df.departure_time_n]
            transfers_df['index'] = transfers_df.index

            if transfers_df.empty and not (current_stop, next_stop) in self.adjacent_stops:
                return []

            if results_df.empty:
                results_df = transfers_df
                results_df.columns = [str(col) + '_0' for col in results_df.columns]
                results_df = results_df.sort_values(by=['departure_time_n_0'])
                results_df = results_df.drop_duplicates(subset='departure_time_c_0', keep='first')
                results_df.rename(columns={'route_id_n_0': 'route_id_0'}, inplace=True)
                results_df.drop(columns=['route_id_c_0'], axis=1, inplace=True)
                if (current_stop, next_stop) in self.adjacent_stops:
                    end_time = start_time + self.adjacent_stops[(current_stop, next_stop)]
                    walking_row = pd.DataFrame({'departure_time_c_0': start_time, 'departure_time_n_0': end_time,
                                                'route_id_0': WALKING_ROUTE_ID,
                                                'index_0': (WALKING_ROUTE_ID, WALKING_ROUTE_ID, WALKING_ROUTE_ID)})
                    results_df = results_df.append(walking_row)
            else:
                if (current_stop, next_stop) in self.adjacent_stops:
                    walking_time = self.adjacent_stops[(current_stop, next_stop)]
                    walking_df = copy(results_df)
                    walking_df['route_id_' + str(i)] = WALKING_ROUTE_ID
                    walking_df['index_' + str(i)] = [(
                        WALKING_ROUTE_ID, WALKING_ROUTE_ID, WALKING_ROUTE_ID)] * len(walking_df)
                    walking_df['departure_time_c_' + str(i)] = walking_df.apply(
                        lambda row: row['departure_time_n_' + str(i-1)], axis=1)
                    walking_df['departure_time_n_' + str(i)] = walking_df.apply(
                        lambda row: row['departure_time_n_' + str(i-1)] + walking_time, axis=1)
                results_df = results_df.assign(c=1)
                results_df = results_df.merge(transfers_df.assign(c=1))
                results_df.drop(columns=['c', 'route_id_c'], axis=1, inplace=True)
                results_df.rename(columns={'departure_time_c': 'departure_time_c_' + str(i),
                                           'departure_time_n': 'departure_time_n_' + str(i),
                                           'route_id_n': 'route_id_' + str(i),
                                           'index': 'index_' + str(i)},
                                  inplace=True)
                results_df = results_df[
                    results_df['departure_time_n_' + str(i - 1)] < results_df['departure_time_c_' + str(i)]]
                if (current_stop, next_stop) in self.adjacent_stops:
                    results_df = results_df.append(walking_df)
                results_df = results_df.sort_values(by=['departure_time_n_' + str(i)])
                results_df = results_df.drop_duplicates(subset='departure_time_c_0', keep='first')

        for row in results_df.itertuples():
            result = []
            for i in range(len(path) - 1):
                route_id = row[4 * i + 3]
                departure_time = row[4 * i + 1]
                arrival_time = row[4 * i + 2]
                result.append((route_id, path[i], path[i+1], departure_time, arrival_time))
            results.append(result)
        return results

    def get_paths(self, start_node, end_node):
        if start_node == end_node:
            return []
        if end_node not in self.paths[start_node]:
            self.paths[start_node][end_node] = self.calculate_paths(start_node, end_node)
        return self.paths[start_node][end_node]

    def calculate_paths(self, start_node_id: int, end_node_id: int):
        def resolve_neighbor(node_id, neighbor_id, weight, path, routes, graph):
            n_weight = weight + graph.edges[node_id, neighbor_id]['weight']
            n_priority = n_weight + self.distances[neighbor_id][end_node_id]
            n_path = copy(path)
            n_path.append(neighbor_id)
            n_routes = copy(routes)
            route = graph.edges[node_id, neighbor_id]['route_ids']
            if self.is_redundant(n_routes, route):
                return
            n_routes.append(route)
            if (n_routes, neighbor_id) not in routes_dict:
                routes_dict.append((n_routes, neighbor_id))
                queue.put((n_priority, n_weight, neighbor_id, n_path, n_routes))

        queue = PriorityQueue()
        count = 0
        paths = []
        costs = []
        routes_dict = []
        routes_to_node = {}
        max_priority = self.distances[start_node_id][end_node_id] * FLOYD_SOLVER_MAX_PRIORITY_MULTIPLIER
        priority = 0


        last_hubs = []
        if end_node_id not in self.kernelized_graph.nodes:
            for neighbor_id in self.graph.neighbors(end_node_id):
                if neighbor_id in self.kernelized_graph.nodes:
                    last_hubs.append(neighbor_id)

        if start_node_id in self.kernelized_graph.nodes:
            queue.put((0, 0, start_node_id, [start_node_id], []))
        else:
            for neighbor_id in self.graph.neighbors(start_node_id):
                if neighbor_id in self.kernelized_graph.nodes:
                    resolve_neighbor(start_node_id, neighbor_id, 0, [start_node_id], [],  self.graph)

        while not queue.empty() and priority <= max_priority and len(paths) <= FLOYD_SOLVER_MAX_PATHS:
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
            if node_id == end_node_id:
                count = count + 1
                paths.append(path)
                costs.append(priority)
                continue
            if node_id in last_hubs:
                resolve_neighbor(node_id, end_node_id, weight, path, routes, self.graph)
            for neighbor_id in self.kernelized_graph.neighbors(node_id):
                resolve_neighbor(node_id, neighbor_id, weight, path, routes, self.kernelized_graph)

        return paths

    def is_redundant(self, n_routes: List[tuple], route: tuple):
        if not n_routes:
            return False
        index = len(n_routes) - 1
        last_route = n_routes[index]
        if set(last_route).issubset(route) or set(route).issubset(last_route):
            return True
        return False
