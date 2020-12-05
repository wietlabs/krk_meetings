import random
import time

import pandas as pd

from src.config import FloydDataPaths
from src.data_classes.MeetingQuery import MeetingQuery
from src.solver.MeetingSolver import MeetingSolver
from src.utils import load_pickle


def set_priority():
    import win32api, win32con, win32process
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)


def create_chart_pickle():
    stops_df = load_pickle(FloydDataPaths.stops_df.value)
    stops = list(stops_df['stop_name'])

    solver = MeetingSolver()
    solver.data_manager.update_data()
    solver.update_data()

    def gen(samples=10000, max_participants_count=20, metric='square'):
        for _ in range(samples):
            participants_count = random.randint(1, max_participants_count)
            start_stops = random.sample(stops, participants_count)
            query = MeetingQuery(0, start_stops, metric)

            start_time = time.perf_counter_ns()
            result = solver.find_meeting_points(query)
            end_time = time.perf_counter_ns()

            execution_time = (end_time - start_time) * 1e-9
            yield participants_count, execution_time
            time.sleep(0.001)

    df = pd.DataFrame(gen(), columns=['participants_count', 'execution_time'])
    pd.to_pickle(df, 'data/MeetingSolverPerformance.pickle')


if __name__ == "__main__":
    set_priority()
    create_chart_pickle()
