import unittest
from datetime import datetime, timedelta
from pathlib import Path

import networkx as nx
from ddt import ddt, data, unpack
from enum import Enum

from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_classes.ConnectionResults import ConnectionResults
from src.data_classes.Walk import Walk
from src.solver.ConnectionSolver import ConnectionSolver
import itertools
RESOURCES_DIR_PATH = Path(__file__).parent / 'resources'


class FloydDataPath(Enum):
    floyd_graph = RESOURCES_DIR_PATH / "floyd_graph.pickle"
    kernelized_floyd_graph = RESOURCES_DIR_PATH / "kernelized_floyd_graph.pickle"
    distances = RESOURCES_DIR_PATH / "distances.pickle"
    day_to_services_dict = RESOURCES_DIR_PATH / "day_to_services_dict.pickle"
    stop_times_0_dict = RESOURCES_DIR_PATH / "stop_times_0_dict.pickle"
    stop_times_24_dict = RESOURCES_DIR_PATH / "stop_times_24_dict.pickle"
    routes_to_stops_dict = RESOURCES_DIR_PATH / "routes_to_stops_dict.pickle"
    adjacent_stops = RESOURCES_DIR_PATH / "adjacent_stops.pickle"
    stops_df = RESOURCES_DIR_PATH / "stops_df.pickle"
    routes_df = RESOURCES_DIR_PATH / "routes_df.pickle"
    stops_df_by_name = RESOURCES_DIR_PATH / "stops_df_by_name.pickle"
    api_walking_distances = RESOURCES_DIR_PATH / "api_walking_distances.pickle"
    exception_days = RESOURCES_DIR_PATH / "exception_days.pickle"


sample_queries = [{"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Krzeszowice Dworzec Autobusowy', "end_stop_name": 'Wolica Most'}]

@ddt
class ConnectionSolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection_solver = ConnectionSolver(data_path=FloydDataPath)
        cls.connection_solver.data_manager.update_data()

    @data(*itertools.product(sample_queries))
    @unpack
    def test_connection_result_not_empty(self, query):
        query["query_id"] = 1
        connection_query = ConnectionQuery.from_dict(query)
        connection_results: ConnectionResults = self.connection_solver.find_connections(connection_query)
        self.assertNotEqual(len(connection_results.connections), 0)

    @data(*itertools.product([{"start_datetime": "2020-11-19 12:00:00", "start_stop_name": 'Jubilat', "end_stop_name": 'Kostrze Szkoła'}]))
    @unpack
    def test_connection_has_walking_edge(self, query):
        query["query_id"] = 1
        connection_query = ConnectionQuery.from_dict(query)
        connection_results: ConnectionResults = self.connection_solver.find_connections(connection_query)
        connections = connection_results.connections
        for connection in connections:
            for action in connection.actions:
                if isinstance(action, Walk):
                    return
        self.fail()

    @data(*itertools.product(
        [({"start_datetime": "2020-11-19 12:00:00", "start_stop_name": 'Jubilat', "end_stop_name": 'Kostrze Szkoła'}, 60),
         ({"start_datetime": "2020-11-14 23:00:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Nowy Bieżanów P+R'}, 120)]))
    @unpack
    def test_connection_duration(self, parameters):
        query, duration = parameters
        query["query_id"] = 1
        connection_query = ConnectionQuery.from_dict(query)
        connection_results: ConnectionResults = self.connection_solver.find_connections(connection_query)
        connections = connection_results.connections
        for connection in connections:
            if connection.end_datetime - connection.start_datetime < timedelta(minutes=duration):
                return
        self.fail()

    @data(*itertools.product(
        [({"start_datetime": "2020-11-22 12:00:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Jerzmanowskiego'},
          {"start_datetime": "2020-12-26 12:00:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Jerzmanowskiego'})]))
    @unpack
    def test_exception_days(self, queries):
        query_1, query_2 = queries
        query_1["query_id"] = 1
        query_2["query_id"] = 2
        connection_query = ConnectionQuery.from_dict(query_1)
        connection_results_1 = self.connection_solver.find_connections(connection_query)
        connection_results_1 = [[(transfer.start_stop_name, transfer.end_stop_name, transfer.route_name, transfer.headsign)
                                 for transfer in connection.transfers] for connection in connection_results_1.connections]

        connection_query = ConnectionQuery.from_dict(query_2)
        connection_results_2 = self.connection_solver.find_connections(connection_query)
        connection_results_2 = [[(transfer.start_stop_name, transfer.end_stop_name, transfer.route_name, transfer.headsign)
                                 for transfer in connection.transfers] for connection in connection_results_2.connections]
        self.assertEqual(connection_results_1, connection_results_2)

    @data(*itertools.product(
        [({"start_datetime": "2020-11-22 12:00:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Jerzmanowskiego'},
          {"start_datetime": "2020-11-23 12:00:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Jerzmanowskiego'})]))
    @unpack
    def test_different_services(self, queries):
        query_1, query_2 = queries
        query_1["query_id"] = 1
        query_2["query_id"] = 2
        connection_query = ConnectionQuery.from_dict(query_1)
        connection_results_1 = self.connection_solver.find_connections(connection_query)
        connection_results_1 = [[(action.start_stop_name, action.end_stop_name)
                                 for action in connection.actions] for connection in connection_results_1.connections]

        connection_query = ConnectionQuery.from_dict(query_2)
        connection_results_2 = self.connection_solver.find_connections(connection_query)
        connection_results_2 = [[(action.start_stop_name, action.end_stop_name)
                                 for action in connection.actions] for connection in connection_results_2.connections]
        self.assertNotEqual(connection_results_1, connection_results_2)

    @data(*itertools.product([({"start_datetime": "2020-11-19 12:00:00", "start_stop_name": 'Górka Narodowa Wschód', "end_stop_name": 'Wieliczka Miasto'}, ["503", "304"])]))
    @unpack
    def test_particular_connection_exists(self, parameters):
        query, exppected_route_names = parameters
        query["query_id"] = 1
        connection_query = ConnectionQuery.from_dict(query)
        connection_results: ConnectionResults = self.connection_solver.find_connections(connection_query)
        connections = connection_results.connections
        for connection in connections:
            route_names = [transfer.route_name for transfer in connection.transfers]
            if route_names == exppected_route_names:
                return
        self.fail()


if __name__ == '__main__':
    unittest.main()
