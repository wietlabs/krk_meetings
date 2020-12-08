import random
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import FloydDataPaths, DATETIME_FORMAT
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.SequenceQuery import SequenceQuery
from src.data_provider.data_provider_utils import get_walking_distance
from src.solver.ConnectionSolver import ConnectionSolver
from src.solver.MeetingSolver import MeetingSolver
from src.solver.SequenceSolver import SequenceSolver
from src.utils import load_pickle


def set_priority():
    import win32api, win32con, win32process
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)


def random_meeting_query(stops_df, metric='square'):
    participants_count = random.randint(1, 30)
    sample = stops_df.sample(participants_count)
    start_stops = list(sample['stop_name'])
    query = MeetingQuery(0, start_stops, metric)
    return participants_count, query


def random_sequence_query(stops_df):
    stops_count = random.randint(1, 8)
    sample = stops_df.sample(stops_count + 2)
    sequence_stops = list(sample['stop_name'])
    start_stop_name, *stops_to_visit, end_stop_name = sequence_stops
    query = SequenceQuery(0, start_stop_name, end_stop_name, stops_to_visit)
    return stops_count, query


def random_connection_query(stops_df):
    sample = stops_df.sample(2)
    start_stop_name, end_stop_name = list(sample['stop_name'])
    start_stop_lat, end_stop_lat = list(sample['stop_lat'])
    start_stop_lon, end_stop_lon = list(sample['stop_lon'])
    distance = get_walking_distance(start_stop_lon, start_stop_lat, end_stop_lon, end_stop_lat)
    query = ConnectionQuery(0, datetime.strptime("2020-05-24 12:00:00", DATETIME_FORMAT), start_stop_name,
                            end_stop_name)
    return distance/1000, query


def random_connection_path_query(stops_df):
    sample = stops_df.sample(2)
    start_stop_id, end_stop_id = list(sample.index)
    start_stop_lat, end_stop_lat = list(sample['stop_lat'])
    start_stop_lon, end_stop_lon = list(sample['stop_lon'])
    distance = get_walking_distance(start_stop_lon, start_stop_lat, end_stop_lon, end_stop_lat)
    query = start_stop_id, end_stop_id
    return distance/1000, query


def create_connection_pickle(gen):
    df = pd.DataFrame(gen(), columns=['distance_km', 'execution_time'])
    pd.to_pickle(df, 'data/connection_solver_performance.pickle')


def create_connection_path_pickle(gen):
    df = pd.DataFrame(gen(), columns=['distance_km', 'execution_time'])
    pd.to_pickle(df, 'data/connection_solver_path_performance.pickle')


def create_meeting_pickle(gen):
    df = pd.DataFrame(gen(), columns=['participants_count', 'execution_time'])
    pd.to_pickle(df, 'data/meeting_solver_performance.pickle')


def create_sequence_pickle(gen):
    df = pd.DataFrame(gen(), columns=['stops_count', 'execution_time'])
    pd.to_pickle(df, 'data/sequence_solver_performance.pickle')


def create_chart_pickle(samples, random_query, create_pickle, solver_function):
    stops_df = load_pickle(FloydDataPaths.stops_df.value)

    def gen():
        for _ in range(samples):
            index, query = random_query(stops_df)
            start_time = time.perf_counter_ns()
            result = solver_function(query)
            end_time = time.perf_counter_ns()
            execution_time = (end_time - start_time) * 1e-9
            yield index, execution_time
            time.sleep(0.001)

    create_pickle(gen)


def generate_meetings_pickle(samples):
    solver = MeetingSolver()
    solver.data_manager.update_data()
    solver.update_data()
    create_chart_pickle(samples, random_meeting_query, create_meeting_pickle, solver.find_meeting_points)


def generate_sequence_pickle(samples):
    solver = SequenceSolver()
    solver.data_manager.update_data()
    solver.update_data()
    create_chart_pickle(samples, random_sequence_query, create_sequence_pickle, solver.find_best_sequence)


def generate_connection_pickle(samples):
    solver = ConnectionSolver()
    solver.data_manager.update_data()
    solver.update_data()
    create_chart_pickle(samples, random_connection_query, create_connection_pickle, solver.find_connections)


def generate_connection_path_pickle(samples):
    solver = ConnectionSolver()
    solver.data_manager.update_data()
    solver.update_data()
    calculate_paths = lambda query: solver.calculate_paths(query[0], query[1])
    create_chart_pickle(samples, random_connection_path_query, create_connection_path_pickle, calculate_paths)


if __name__ == "__main__":
    Path('data').mkdir(parents=True, exist_ok=True)
    set_priority()
    generate_meetings_pickle(1000)
    generate_sequence_pickle(1000)
    generate_connection_path_pickle(1000)
    generate_connection_pickle(1000)
