import time
from src.config import FloydDataPaths
import random
import pandas as pd

from src.data_classes.MeetingQuery import MeetingQuery
from src.solver.MeetingSolver import MeetingSolver
from src.utils import load_pickle


def create_chart_pickle():
    stops_df = load_pickle(FloydDataPaths.stops_df.value)
    stops = [{"name": stop[1], "latitude": stop[2], "longitude": stop[3]} for stop in stops_df.itertuples()]
    stops = [s['name'] for s in stops]
    len_stops = len(stops)
    solver = MeetingSolver()
    solver.data_manager.update_data()
    solver.update_data()

    participants_list = []
    time_list = []
    for participants in range(1, 31):
        start_time = time.time()
        for _ in range(100):
            try:
                meeting_points = solver.find_meeting_points(MeetingQuery(0, [stops[random.randint(0, len_stops-1)]
                                                                             for _ in range(participants)], "square"))
            except:
                pass
        execution_time = time.time() - start_time
        participants_list.append(participants)
        time_list.append(execution_time/100)

    data = {'participants': participants_list, 'time': time_list}
    result_df = pd.DataFrame.from_dict(data)
    pd.to_pickle(result_df, "MeetingSolverPerformance.pickle")
    print(participants_list)
    print(time_list)
    print(result_df)


if __name__ == "__main__":
    create_chart_pickle()
