from src.config import ErrorCodes
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.solver import solver_utils
from src.solver.IMeetingSolver import IMeetingSolver
from src.data_managers.MeetingDataManager import MeetingDataManager


class MeetingSolver(IMeetingSolver):
    def __init__(self, ):
        self.data_manager = MeetingDataManager()
        self.distances = None
        self.stops_df = None
        self.stops_df_by_name = None

        self.data_manager.start()
        self.data_manager.update_data()
        self.update_data()

    def update_data(self):
        if not self.data_manager.up_to_date:
            data = self.data_manager.get_updated_data()
            self.distances = data["distances"]
            self.stops_df = data["stops_df"]
            self.stops_df_by_name = data["stops_df_by_name"]

    def find_meeting_points(self, query: MeetingQuery) -> MeetingResults:
        self.update_data()
        start_stop_ids = [solver_utils.get_stop_id_by_name(stop_name, self.stops_df_by_name) for stop_name in query.start_stop_names]
        if None in start_stop_ids:
            bad_stop_names = [stop[0] for stop in zip(query.start_stop_names, start_stop_ids) if stop[1] is None]
            error = ErrorCodes.BAD_STOP_NAMES_IN_SEQUENCE.value
            error["text"] = ErrorCodes.BAD_START_STOP_NAMES_IN_MEETING.value["text"].format(bad_stop_names)
            return MeetingResults(query.query_id, error, [])

        if query.metric == 'square':
            metric = lambda l: sum(map(lambda i: i * i, l))
        elif query.metric == 'sum':
            metric = lambda l: sum(l)
        elif query.metric == 'max':
            metric = lambda l: max(l)
        else:
            return None
        meeting_metrics = []
        for end_stop_id in self.distances:
            distances_to_destination = list(map(lambda stop_id: self.distances[stop_id][end_stop_id], start_stop_ids))
            meeting_metrics.append((end_stop_id, metric(distances_to_destination)))
        meeting_metrics.sort(key=lambda x: x[1])
        meeting_points = list(map(lambda x: self.stops_df.at[x[0], 'stop_name'], meeting_metrics[0:10]))
        return MeetingResults(query.query_id, ErrorCodes.OK.value, meeting_points)
