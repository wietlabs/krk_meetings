import datetime
import time
from src.config import FloydDataPaths, DATETIME_FORMAT
import random
import pandas as pd

from src.data_classes.ConnectionQuery import ConnectionQuery
from src.solver.ConnectionSolver import ConnectionSolver
from src.utils import load_pickle


def create_chart_pickle():
    stops_df = load_pickle(FloydDataPaths.stops_df.value)
    stops = [{"name": stop[1], "latitude": stop[2], "longitude": stop[3]} for stop in stops_df.itertuples()]
    stops = [s['name'] for s in stops]
    len_stops = len(stops)
    solver = ConnectionSolver()
    solver.data_manager.update_data()
    solver.update_data()
    solver.data_manager.update_delays_df()
    solver.update_delays_df()

    # connection_result_dict = {}
    start_stops = []
    end_stops = []
    times = []
    all_start_time = time.time()
    counter = 0
    while counter < 1000:
        stop_1 = stops[random.randint(0, len_stops-1)]
        stop_2 = stops[random.randint(0, len_stops-1)]
        start_time = time.time()
        try:
            connections = solver.find_connections(ConnectionQuery(0, datetime.datetime.strptime("2020-05-24 12:00:00", DATETIME_FORMAT), stop_1, stop_2))
            if not connections.connections:
                continue
            counter += 1
        except:
            pass
        execution_time = time.time() - start_time
        start_stops.append(stop_1)
        end_stops.append(stop_2)
        times.append(execution_time)
        # key = int(execution_time * 10)/10 if execution_time <= 10.0 else 10.0
        # if key in connection_result_dict:
        #     connection_result_dict[key] += 0.1
        # else:
        #     connection_result_dict[key] = 0.1

    # print(connection_result_dict)
    # print(time.time() - all_start_time)

    # time_list = [key for key in connection_result_dict.keys()]
    # count_list = [connection_result_dict[key] for key in connection_result_dict.keys()]
    # data = {'time': time_list, 'count(%)': count_list}
    data = {'execution_time': times, 'start_stop_name': start_stops, 'end_stop_name': end_stops}
    result_df = pd.DataFrame.from_dict(data)
    pd.to_pickle(result_df, "ConnectionSolverPerformance2.pickle")
    print(result_df)


if __name__ == "__main__":
    create_chart_pickle()
