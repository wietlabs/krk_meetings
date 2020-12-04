import time
from src.config import FloydDataPaths
import random
import pandas as pd

from src.data_classes.SequenceQuery import SequenceQuery
from src.solver.SequenceSolver import SequenceSolver
from src.utils import load_pickle


def create_chart_pickle():
    stops_df = load_pickle(FloydDataPaths.stops_df.value)
    stops = [{"name": stop[1], "latitude": stop[2], "longitude": stop[3]} for stop in stops_df.itertuples()]
    stops = [s['name'] for s in stops]
    len_stops = len(stops)
    solver = SequenceSolver()
    solver.data_manager.update_data()
    solver.update_data()

    stops_to_visit_list = []
    time_list = []
    for stops_to_visit in range(1, 11):
        start_time = time.time()
        p_range = 1000 if stops_to_visit < 6 else 100 if stops_to_visit < 9 else 10
        for _ in range(p_range):
            try:
                best_sequence = solver.find_best_sequence(SequenceQuery(0, stops[random.randint(0, len_stops-1)],
                                                                         stops[random.randint(0, len_stops-1)],
                                                                         [stops[random.randint(0, len_stops-1)]
                                                                             for _ in range(stops_to_visit)]))
            except:
                pass
        execution_time = time.time() - start_time
        stops_to_visit_list.append(stops_to_visit)
        time_list.append(execution_time/p_range)

    data = {'stops_to_visit': stops_to_visit_list, 'time': time_list}
    result_df = pd.DataFrame.from_dict(data)
    pd.to_pickle(result_df, "SequenceSolverPerformance.pickle")
    print(stops_to_visit_list)
    print(time_list)
    print(result_df)


if __name__ == "__main__":
    create_chart_pickle()
