import unittest
from datetime import datetime, timedelta

from ddt import ddt, data, unpack

from krk_meetings.config import DATETIME_FORMAT
from krk_meetings.data_classes.ConnectionQuery import ConnectionQuery
from krk_meetings.data_classes.ConnectionResults import ConnectionResults
from krk_meetings.data_classes.Walk import Walk
from krk_meetings.solver.ConnectionSolver import ConnectionSolver
from krk_meetings.solver.tests.config import FloydDataPathsTest


@ddt
class ConnectionSolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection_solver = ConnectionSolver(data_path=FloydDataPathsTest)
        cls.connection_solver.data_manager.update_data()

    @data(
        {"start_datetime": "2020-11-19 12:00:00", "start_stop_name": "Krzeszowice Dworzec Autobusowy", "end_stop_name": "Wolica Most"},
    )
    def test_connection_result_not_empty(self, query):
        connection_query = ConnectionQuery.from_dict(query)
        connection_results: ConnectionResults = self.connection_solver.find_connections(connection_query)
        self.assertNotEqual(len(connection_results.connections), 0)

    @data(
        {"start_datetime": "2020-11-19 12:00:00", "start_stop_name": "Jubilat", "end_stop_name": "Kostrze Szkoła"},
    )
    def test_connection_has_walking_edge(self, query):
        connection_query = ConnectionQuery.from_dict(query)
        connection_results: ConnectionResults = self.connection_solver.find_connections(connection_query)
        connections = connection_results.connections
        for connection in connections:
            for action in connection.actions:
                if isinstance(action, Walk):
                    return
        self.fail()

    @data(
        ({"start_datetime": "2020-11-19 12:00:00", "start_stop_name": "Jubilat", "end_stop_name": "Kostrze Szkoła"}, 60),
        ({"start_datetime": "2020-11-14 23:00:00", "start_stop_name": "Czerwone Maki P+R", "end_stop_name": "Nowy Bieżanów P+R"}, 120),
    )
    @unpack
    def test_connection_duration(self, query, duration):
        connection_query = ConnectionQuery.from_dict(query)
        connection_results: ConnectionResults = self.connection_solver.find_connections(connection_query)
        connections = connection_results.connections
        for connection in connections:
            if connection.end_datetime - connection.start_datetime < timedelta(minutes=duration):
                return
        self.fail()

    @data(
        ({"start_datetime": "2020-11-22 12:00:00", "start_stop_name": "Czerwone Maki P+R", "end_stop_name": "Jerzmanowskiego"},
         {"start_datetime": "2020-12-26 12:00:00", "start_stop_name": "Czerwone Maki P+R", "end_stop_name": "Jerzmanowskiego"}),
    )
    @unpack
    def test_exception_days(self, query_1, query_2):
        connection_query = ConnectionQuery.from_dict(query_1)
        connection_results_1 = self.connection_solver.find_connections(connection_query)
        connection_results_1 = [[(transfer.start_stop_name, transfer.end_stop_name, transfer.route_name, transfer.headsign)
                                 for transfer in connection.transfers] for connection in connection_results_1.connections]

        connection_query = ConnectionQuery.from_dict(query_2)
        connection_results_2 = self.connection_solver.find_connections(connection_query)
        connection_results_2 = [[(transfer.start_stop_name, transfer.end_stop_name, transfer.route_name, transfer.headsign)
                                 for transfer in connection.transfers] for connection in connection_results_2.connections]
        self.assertEqual(connection_results_1, connection_results_2)

    @data(
        ({"start_datetime": "2020-11-22 12:00:00", "start_stop_name": "Czerwone Maki P+R", "end_stop_name": "Jerzmanowskiego"},
         {"start_datetime": "2020-11-23 12:00:00", "start_stop_name": "Czerwone Maki P+R", "end_stop_name": "Jerzmanowskiego"}),
    )
    @unpack
    def test_different_services(self, query_1, query_2):
        connection_query = ConnectionQuery.from_dict(query_1)
        connection_results_1 = self.connection_solver.find_connections(connection_query)
        connection_results_1 = [[(action.start_stop_name, action.end_stop_name)
                                 for action in connection.actions] for connection in connection_results_1.connections]

        connection_query = ConnectionQuery.from_dict(query_2)
        connection_results_2 = self.connection_solver.find_connections(connection_query)
        connection_results_2 = [[(action.start_stop_name, action.end_stop_name)
                                 for action in connection.actions] for connection in connection_results_2.connections]
        self.assertNotEqual(connection_results_1, connection_results_2)

    @data(
        ({"start_datetime": "2020-11-19 12:00:00", "start_stop_name": "Górka Narodowa Wschód", "end_stop_name": "Wieliczka Miasto"}, ["503", "304"]),
        ({"start_datetime": "2020-11-19 12:00:00", "start_stop_name": "Kawiory", "end_stop_name": "Azory"}, ["173"]),
        ({"start_datetime": "2020-11-19 12:00:00", "start_stop_name": "Kawiory", "end_stop_name": "Azory"}, ["144"]),
    )
    @unpack
    def test_particular_connection_exists_by_routes(self, query, expected_route_names):
        connection_query = ConnectionQuery.from_dict(query)
        connection_results: ConnectionResults = self.connection_solver.find_connections(connection_query)
        connections = connection_results.connections
        for connection in connections:
            route_names = [transfer.route_name for transfer in connection.transfers]
            if route_names == expected_route_names:
                return
        self.fail()

    @data(
        ({"start_datetime": "2020-11-19 12:00:00", "start_stop_name": "Cracovia Stadion", "end_stop_name": "ZOO"}, "2020-11-19 12:04:00", "2020-11-19 12:20:00"),
        ({"start_datetime": "2020-11-19 12:14:00", "start_stop_name": "Rondo Grunwaldzkie", "end_stop_name": "Rynek Dębnicki"}, "2020-11-19 12:15:00", "2020-11-19 12:17:00"),
        ({"start_datetime": "2020-11-19 12:00:00", "start_stop_name": "Os. Podwawelskie", "end_stop_name": "Rondo Grunwaldzkie"}, "2020-11-19 12:10:00", "2020-11-19 12:12:00"),
    )
    @unpack
    def test_particular_connection_exists_by_times(self, query, start_datetime, end_datetime):
        start_datetime = datetime.strptime(start_datetime, DATETIME_FORMAT)
        end_datetime = datetime.strptime(end_datetime, DATETIME_FORMAT)
        connection_query = ConnectionQuery.from_dict(query)
        connection_results: ConnectionResults = self.connection_solver.find_connections(connection_query)
        connections = connection_results.connections
        for connection in connections:
            if connection.start_datetime == start_datetime and connection.end_datetime == end_datetime:
                return
        self.fail()


if __name__ == "__main__":
    unittest.main()
