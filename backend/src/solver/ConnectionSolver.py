from copy import copy
from queue import PriorityQueue
from typing import List
from itertools import chain
import pandas as pd
from datetime import datetime, timedelta
import time
from src.data_classes.Connection import Connection
from src.data_classes.ConnectionResults import ConnectionResults
from src.data_classes.Walk import Walk
from src.solver import solver_utils
from src.solver.ConnectionSolverConfiguration import ConnectionSolverConfiguration
from src.data_managers.ConnectionDataManager import ConnectionDataManager
from src.solver.solver_utils import get_services
from src.utils import time_to_int
from src.solver.interfaces.IConnectionSolver import IConnectionSolver
from src.data_classes.Transfer import Transfer
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.config import ErrorCodes, DEFAULT_CONNECTION_SOLVER_CONFIGURATION, FloydDataPaths


class ConnectionSolver(IConnectionSolver):
    def __init__(self, configuration: ConnectionSolverConfiguration = DEFAULT_CONNECTION_SOLVER_CONFIGURATION, data_path=FloydDataPaths):
        self.configuration = configuration
        self.data_manager = ConnectionDataManager(data_path)
        self.graph = None
        self.kernelized_graph = None
        self.distances = None
        self.stops_df = None
        self.routes_df = None
        self.stops_df_by_name = None
        self.current_stop_times = None
        self.next_stop_times = None
        self.previous_stop_times = None
        self.paths = None
        self.day_to_services_dict = None
        self.adjacent_stops = None
        self.routes_to_stops_dict = None
        self.exception_days_dict = None
        self.last_data_update = None

    def start(self):
        self.data_manager.start()
        self.update_data()

    def update_data(self):
        data = self.data_manager.get_updated_data()
        self.graph = data["graph"]
        self.kernelized_graph = data["kernelized_graph"]
        self.distances = data["distances"]
        self.stops_df = data["stops_df"]
        self.routes_df = data["routes_df"]
        self.stops_df_by_name = data["stops_df_by_name"]
        self.current_stop_times = data["current_stop_times"]
        self.next_stop_times = data["next_stop_times"]
        self.previous_stop_times = data["previous_stop_times"]
        self.day_to_services_dict = data["day_to_services_dict"]
        self.adjacent_stops = data["adjacent_stops"]
        self.routes_to_stops_dict = data["routes_to_stops_dict"]
        self.exception_days_dict = data["exception_days_dict"]
        self.paths = dict()
        for node in self.graph.nodes():
            self.paths[node] = dict()
        self.last_data_update = self.data_manager.last_data_update

    def find_connections(self, query: ConnectionQuery) -> ConnectionResults:
        print("ConnectionSolver: finding connections")
        if self.last_data_update is None or self.last_data_update < self.data_manager.last_data_update:
            self.update_data()
        current_datetime = query.start_datetime
        current_time = time_to_int(current_datetime.time())
        start_stop_id = solver_utils.get_stop_id_by_name(query.start_stop_name, self.stops_df_by_name)
        if start_stop_id is None:
            return ConnectionResults(query.query_id, ErrorCodes.BAD_START_STOP_NAME.value, [])
        end_stop_id = solver_utils.get_stop_id_by_name(query.end_stop_name, self.stops_df_by_name)
        if end_stop_id is None:
            return ConnectionResults(query.query_id, ErrorCodes.BAD_END_STOP_NAME.value, [])

        paths = self.get_paths(start_stop_id, end_stop_id)
        connections = []
        connection_dfs = {}
        first_partition = True
        for earliest_start_time in range(current_time, current_time + self.configuration.max_searching_time,
                                         self.configuration.partition_time):
            partition_connections = self.find_partition_connections(paths, earliest_start_time, current_datetime,
                                                                    connection_dfs)
            if not first_partition:
                partition_connections = [c for c in partition_connections if not c.walk_only]
            partition_connections.sort(
                key=lambda c: c.actions[0].start_datetime if c.walk_only else c.first_transfer.start_datetime)
            connections.extend(partition_connections)
            if len(connections) >= self.configuration.number_of_connections_returned:
                break
            first_partition = False
        return ConnectionResults(query.query_id, ErrorCodes.OK.value,
                                 connections[0: self.configuration.number_of_connections_returned])

    def find_partition_connections(self, paths, earliest_start_time, current_datetime, connection_dfs):
        connections = []
        for path in paths:
            lastest_start_time = earliest_start_time + self.configuration.max_travel_time
            results = self.find_routes(path, earliest_start_time, lastest_start_time, current_datetime, connection_dfs)
            if results is not None:
                for result in results:
                    transfers = []
                    for transfer in result:
                        route_id, current_stop_id, next_stop_id, departure_time, arrival_time = transfer
                        current_stop_name = solver_utils.get_stop_name_by_id(current_stop_id, self.stops_df)
                        next_stop_name = solver_utils.get_stop_name_by_id(next_stop_id, self.stops_df)
                        format_datetime = datetime(current_datetime.year, current_datetime.month, current_datetime.day)
                        start_datetime = format_datetime + timedelta(seconds=departure_time)
                        end_datetime = format_datetime + timedelta(seconds=arrival_time)
                        if route_id != self.configuration.walking_route_id:
                            route_name = solver_utils.get_route_name_by_id(route_id, self.routes_df)
                            headsign = solver_utils.get_headsign_by_id(route_id, self.routes_df)
                            stops = solver_utils.get_stop_list(route_id, current_stop_id, next_stop_id, self.stops_df,
                                                               self.routes_to_stops_dict)
                            transfers.append(
                                Transfer(route_name, headsign, current_stop_name, next_stop_name, start_datetime,
                                         end_datetime, stops))
                        else:
                            duration_in_minutes = int((arrival_time - departure_time) / 60)
                            transfers.append(Walk(current_stop_name, next_stop_name, duration_in_minutes,
                                                  start_datetime, end_datetime))

                    connection = Connection(transfers)
                    connections.append(connection)
        return connections

    def find_routes(self, path: List[int], earliest_start_time: int, latest_start_time: int, start_datetime: datetime,
                    connection_dfs: dict) -> list:
        current_services = get_services(start_datetime, self.day_to_services_dict, self.exception_days_dict)
        previous_services = get_services(start_datetime - timedelta(days=1), self.day_to_services_dict, self.exception_days_dict)
        next_services = get_services(start_datetime + timedelta(days=1), self.day_to_services_dict, self.exception_days_dict)
        results_df = self.find_result_routes_df(earliest_start_time, latest_start_time, path, current_services,
                                                next_services, previous_services, connection_dfs)
        results = []
        for row in results_df.itertuples():
            result = []
            for i in range(len(path) - 1):
                route_id = row[4 * i + 3]
                departure_time = row[4 * i + 1]
                arrival_time = row[4 * i + 2]
                result.append((route_id, path[i], path[i + 1], departure_time, arrival_time))
            results.append(result)
        return results

    def find_result_routes_df(self, start_time: int, end_time: int, path, current_services, next_services,
                              previous_services, connection_dfs: dict) -> pd.DataFrame:
        results_df = pd.DataFrame()
        for i in range(len(path) - 1):
            current_stop = path[i]
            next_stop = path[i + 1]

            cst_df = self.get_stoptimes_for_stop(current_stop, connection_dfs, current_services, next_services, previous_services)
            nst_df = self.get_stoptimes_for_stop(next_stop, connection_dfs, current_services, next_services, previous_services)

            cst_df = cst_df[start_time <= cst_df.departure_time]
            cst_df = cst_df[cst_df.departure_time < end_time]
            nst_df = nst_df[start_time <= nst_df.departure_time]
            nst_df = nst_df[nst_df.departure_time < end_time]

            transfers_df = cst_df.join(nst_df, how='inner', lsuffix='_c', rsuffix='_n')
            transfers_df = transfers_df[transfers_df.departure_time_c < transfers_df.departure_time_n]
            transfers_df['index'] = transfers_df.index
            if transfers_df.empty and not (current_stop, next_stop) in self.adjacent_stops:
                return pd.DataFrame()

            if results_df.empty:
                results_df = transfers_df
                results_df.columns = [str(col) + '_0' for col in results_df.columns]
                results_df = results_df.sort_values(by=['departure_time_n_0'])
                results_df = results_df.drop_duplicates(subset='departure_time_c_0', keep='first')
                results_df.rename(columns={'route_id_n_0': 'route_id_0'}, inplace=True)
                results_df.drop(columns=['route_id_c_0'], axis=1, inplace=True)
                if (current_stop, next_stop) in self.adjacent_stops:
                    end_time = start_time + self.adjacent_stops[(current_stop, next_stop)]
                    walking_row = pd.DataFrame({
                        'departure_time_c_0': start_time,
                        'departure_time_n_0': end_time,
                        'route_id_0': self.configuration.walking_route_id,
                        'index_0': [self.configuration.walking_index]},
                        index=([self.configuration.walking_index]))
                    results_df = results_df.append(walking_row)
            else:
                if (current_stop, next_stop) in self.adjacent_stops:
                    walking_time = self.adjacent_stops[(current_stop, next_stop)]
                    walking_df = copy(results_df)
                    walking_df = walking_df[
                        walking_df[f'route_id_{str(i - 1)}'] != self.configuration.walking_route_id]
                    if not walking_df.empty:
                        walking_df[f'route_id_{str(i)}'] = self.configuration.walking_route_id
                        walking_df[f'index_{str(i)}'] = [self.configuration.walking_index] * len(walking_df)
                        walking_df[f'departure_time_c_{str(i)}'] = walking_df.apply(
                            lambda row: row[f'departure_time_n_{str(i - 1)}'], axis=1)
                        walking_df[f'departure_time_n_{str(i)}'] = walking_df.apply(
                            lambda row: row[f'departure_time_n_{str(i - 1)}'] + walking_time, axis=1)
                results_df = results_df.assign(c=1)
                results_df = results_df.merge(transfers_df.assign(c=1))
                results_df.drop(columns=['c', 'route_id_c'], axis=1, inplace=True)
                results_df.rename(columns={'departure_time_c': f'departure_time_c_{str(i)}',
                                           'departure_time_n': f'departure_time_n_{str(i)}',
                                           'route_id_n': f'route_id_{str(i)}',
                                           'index': f'index_{str(i)}'},
                                  inplace=True)
                results_df = results_df[results_df[f'departure_time_n_{str(i - 1)}'] < results_df[f'departure_time_c_{str(i)}']]
                if (current_stop, next_stop) in self.adjacent_stops:
                    results_df = results_df.append(walking_df)
                results_df = results_df.sort_values(by=[f'departure_time_n_{str(i)}'])
                results_df = results_df.drop_duplicates(subset='departure_time_c_0', keep='first')
                if results_df.empty:
                    return pd.DataFrame()
        return results_df

    def get_stoptimes_for_stop(self, stop_id, connection_dfs, current_services, next_services, previous_services):
        if stop_id in connection_dfs.keys():
            return connection_dfs[stop_id]

        df = pd.concat(chain([self.current_stop_times[stop_id][service] for service in current_services],
                             [self.next_stop_times[stop_id][service] for service in next_services],
                             [self.previous_stop_times[stop_id][service] for service in previous_services]))
        connection_dfs[stop_id] = df
        return df

    def get_paths(self, start_node, end_node):
        print("ConnectionSolver: getting paths")
        if start_node == end_node:
            return []
        if end_node not in self.paths[start_node]:
            self.paths[start_node][end_node] = self.calculate_paths(start_node, end_node)
        print(f"ConnectionSolver: got paths: {self.paths[start_node][end_node]}")
        return self.paths[start_node][end_node]

    def calculate_paths(self, start_node_id: int, end_node_id: int):
        print("ConnectionSolver: calculating paths")
        calculation_start_time = time.time()

        def get_max_priority(prior):
            return prior * self.configuration.max_priority_multiplier + self.configuration.max_priority_cap

        def get_max_queue_priority(prior):
            return (prior * self.configuration.max_priority_multiplier
                    + self.configuration.max_priority_cap) * self.configuration.path_calculation_boost

        def resolve_neighbor(node_id, neighbor_id, weight, path, routes, graph):
            n_weight = weight + graph.edges[node_id, neighbor_id]['weight']
            n_queue_priority = n_weight + self.distances[neighbor_id][
                end_node_id] * self.configuration.path_calculation_boost
            n_priority = n_weight + self.distances[neighbor_id][
                end_node_id] * self.configuration.max_priority_multiplier
            n_path = copy(path)
            n_path.append(neighbor_id)
            n_routes = copy(routes)
            route = graph.edges[node_id, neighbor_id]['route_ids']
            if self.is_redundant(n_routes, route):
                return

            if n_queue_priority <= max_queue_priority and n_priority <= max_priority and len(n_path) <= self.configuration.max_path_len:
                n_routes.append(route)
                if (n_routes, neighbor_id) not in routes_dict:
                    routes_dict.append((n_routes, neighbor_id))
                    queue.put((n_queue_priority, n_weight, neighbor_id, n_path, n_routes))

        queue = PriorityQueue()
        paths = []
        routes_dict = []
        routes_to_node = {}
        priority_distance = float("inf")
        max_priority = float("inf")
        max_queue_priority = float("inf")

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
                    resolve_neighbor(start_node_id, neighbor_id, 0, [start_node_id], [], self.graph)

        while not queue.empty() and len(paths) <= self.configuration.max_number_of_paths:
            if time.time() > calculation_start_time + self.configuration.max_path_calculation_time:
                break
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
                if priority < max_priority:
                    paths.append(path)
                    if priority < priority_distance:
                        max_priority = get_max_priority(priority_distance)
                        max_queue_priority = get_max_queue_priority(priority_distance)
                        priority_distance = priority
                    continue
            if node_id in last_hubs:
                resolve_neighbor(node_id, end_node_id, weight, path, routes, self.graph)
            for neighbor_id in self.kernelized_graph.neighbors(node_id):
                resolve_neighbor(node_id, neighbor_id, weight, path, routes, self.kernelized_graph)
        if [start_node_id, end_node_id] not in paths:
            paths.append([start_node_id, end_node_id])
        return paths

    def is_redundant(self, n_routes: List[tuple], route: tuple):
        if not n_routes:
            return False
        index = len(n_routes) - 1
        last_route = n_routes[index]
        if set(last_route).issubset(route) or set(route).issubset(last_route):
            return True
        return False


