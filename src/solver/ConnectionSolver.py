from copy import copy
from queue import PriorityQueue
from typing import List
from itertools import chain
import pandas as pd

from src.data_classes.ConnectionResults import ConnectionResults
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.solver.DataUpdater import DataUpdater
from src.utils import *
from src.solver.IConnectionSolver import IConnectionSolver
from src.data_classes.Transfer import Transfer
from src.data_classes.ConnectionQuery import ConnectionQuery

from src.config import FLOYD_SOLVER_SEARCHING_TIME, FLOYD_SOLVER_MAX_PRIORITY_MULTIPLIER, FLOYD_SOLVER_MAX_PATHS, \
    EXCHANGES


def start_connection_solver():
    connection_solver = ConnectionSolver()
    connection_solver.start()


class ConnectionSolver(DataUpdater, IConnectionSolver):
    def __init__(self):
        DataUpdater.__init__(self)
        self.query_consumer = RmqConsumer(EXCHANGES.CONNECTION_QUERY.value, self.consume_transfer_query)
        self.results_producer = RmqProducer(EXCHANGES.CONNECTION_RESULTS.value)

    def start(self):
        DataUpdater.start(self)
        print("ConnectionSolver has started.")
        self.query_consumer.start()

    def stop(self):
        DataUpdater.stop(self)
        self.query_consumer.stop()
        self.results_producer.stop()

    def consume_transfer_query(self, query: ConnectionQuery):
        with self.lock:
            connections = self.find_connections(query)
            self.results_producer.send_msg(connections)

    def find_connections(self, query: ConnectionQuery) -> List[ConnectionResults]:
        current_time = time_to_int(query.start_time)
        current_date = query.start_date
        start_stop_id = self.stops_df_by_name.at[query.start_stop_name, 'stop_id']
        end_stop_id = self.stops_df_by_name.at[query.end_stop_name, 'stop_id']

        paths = self.get_paths(start_stop_id, end_stop_id)
        connections = []
        for path in paths:
            results = self.find_routes(path, current_time, current_date)
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

            if transfers_df.empty:
                return []

            if results_df.empty:
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
                results_df = results_df[
                    results_df['departure_time_n' + str(i - 1)] < results_df['departure_time_c' + str(i)]]
                results_df = results_df.sort_values(by=['departure_time_n' + str(i)])
                results_df = results_df.drop_duplicates(subset='departure_time_c0', keep='first')

        for row in results_df.itertuples():
            result = []
            for i in range(len(path) - 1):
                index = row[3 * i + 3]
                departure_time = row[3 * i + 1]
                arrival_time = row[3 * i + 2]
                result.append((index, path[i], path[i+1], departure_time, arrival_time))
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

        while queue and priority <= max_priority and len(paths) <= FLOYD_SOLVER_MAX_PATHS:
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
