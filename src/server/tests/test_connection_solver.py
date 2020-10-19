import json
import multiprocessing
import time
import random
from unittest import TestCase

import pytest
import requests

from src.config import URL
from src.server.FlaskServer import start_flask_server
from src.rabbitmq.RmqConnectionSolver import start_connection_solver


pytestmark = pytest.mark.skip


def make_request(query_json):
    response = requests.post(URL.CONNECTION.value, json=json.dumps(query_json), timeout=1.0)
    query_id = response.json()
    for _ in range(30):
        response = requests.get(URL.GET.value.format(query_id), json=json.dumps(query_json), timeout=1.0)
        result = response.json()
        if 'connections' in result:
            break
        time.sleep(5)


class ConnectionSolverTests(TestCase):
    query_json = {
        "start_datetime": "2020-05-24 20:00:00",
        "start_stop_name": 'Jubilat',
        "end_stop_name": 'Kostrze Szkoła'
    }
    connection_solver_process = multiprocessing.Process(target=start_connection_solver)
    flask_server_process = multiprocessing.Process(target=start_flask_server)

    def ask_for_one_connection(self):
        response = requests.post(URL.CONNECTION.value, json=json.dumps(self.query_json), timeout=1.0)
        query_id = response.json()
        time.sleep(5)
        response = requests.get(URL.GET.value.format(query_id), json=json.dumps(self.query_json), timeout=1.0)
        result = response.json()
        self.assertTrue("connections" in result)

    def setUp(self):
        self.connection_solver_process.start()
        self.flask_server_process.start()
        time.sleep(20)

    def tearDown(self):
        self.connection_solver_process.terminate()
        self.flask_server_process.terminate()

    def test_post_and_get(self):
        self.ask_for_one_connection()

    #  TODO for now this many requests in such short time is to many
    # def test_connection_solver_multi_process_01_sec(self):
    #     processes = []
    #     for i in range(100):
    #         processes.append(multiprocessing.Process(target=make_request, args=(self.query_json, )))
    #     for process in processes:
    #         process.start()
    #         time.sleep(0.1)
    #     for process in processes:
    #         process.join()
    #     self.ask_for_one_connection()

    def test_connection_solver_multi_process_1_sec(self):
        processes = []
        for i in range(100):
            processes.append(multiprocessing.Process(target=make_request, args=(self.query_json, )))
        for process in processes:
            process.start()
            time.sleep(1)
        for process in processes:
            process.join()
        self.ask_for_one_connection()
