import unittest
from datetime import datetime, timedelta
from ddt import ddt, data, unpack
from src.config import DATETIME_FORMAT
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_classes.ConnectionResults import ConnectionResults
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.data_classes.Walk import Walk
from src.solver.ConnectionSolver import ConnectionSolver
import itertools

from src.solver.MeetingSolver import MeetingSolver
from src.solver.tests.config import TestFloydDataPaths


@ddt
class ConnectionSolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meeting_solver = MeetingSolver(data_path=TestFloydDataPaths)
        cls.meeting_solver.data_manager.update_data()

    @data(*itertools.product([({"start_stop_names": ["Kampus UJ", "AGH / UR", "Prokocim Szpital"], "metric": "square"}, "Rondo Matecznego"),
                              ({"start_stop_names": ["Czerwone Maki P+R", "Skotniki Szkoła", "Chmieleniec"], "metric": "square"}, "Czerwone Maki P+R")]))
    @unpack
    def test_meeting_place(self, parameters):
        query, meeting_point = parameters
        query["query_id"] = 1
        meeting_results = MeetingQuery.from_dict(query)
        connection_results: MeetingResults = self.meeting_solver.find_meeting_points(meeting_results)
        for stop in connection_results.meeting_points:
            if stop["name"] == meeting_point:
                return
        self.fail()

    def test_metrics(self):
        sum_query = MeetingQuery.from_dict({"start_stop_names": ["Kampus UJ", "AGH / UR", "Prokocim Szpital"], "metric": "sum"})
        square_query = MeetingQuery.from_dict({"start_stop_names": ["Kampus UJ", "AGH / UR", "Prokocim Szpital"], "metric": "square"})
        max_query = MeetingQuery.from_dict({"start_stop_names": ["Kampus UJ", "AGH / UR", "Prokocim Szpital"], "metric": "max"})
        sum_results: MeetingResults = self.meeting_solver.find_meeting_points(sum_query)
        square_results: MeetingResults = self.meeting_solver.find_meeting_points(square_query)
        max_results: MeetingResults = self.meeting_solver.find_meeting_points(max_query)
        self.assertNotEquals(sum_results, square_results)
        self.assertNotEquals(square_results, max_results)
        self.assertNotEquals(sum_results, max_results)