from src.config import ErrorCodes
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.solver import solver_utils
from src.solver.IMeetingSolver import IMeetingSolver
from src.data_managers.MeetingDataManager import MeetingDataManager
from src.solver.solver_utils import stop_data


class MeetingSolver(IMeetingSolver):
    def __init__(self, ):
        self.data_manager = MeetingDataManager()
        self.distances = None
        self.stops_df = None
        self.stops_df_by_name = None
        self.last_data_update = None

        self.data_manager.start()
        self.update_data()

    def update_data(self):
        data = self.data_manager.get_updated_data()
        self.distances = data["distances"]
        self.stops_df = data["stops_df"]
        self.stops_df_by_name = data["stops_df_by_name"]
        self.last_data_update = self.data_manager.last_data_update

    def find_meeting_points(self, query: MeetingQuery) -> MeetingResults:
        if self.last_data_update < self.data_manager.last_data_update:
            self.update_data()
        start_stop_ids = [solver_utils.get_stop_id_by_name(stop_name, self.stops_df_by_name) for stop_name in query.start_stop_names]
        if None in start_stop_ids:
            return MeetingResults(query.query_id, ErrorCodes.BAD_STOP_NAMES_IN_SEQUENCE.value, [])

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
            distances_to_destination = [self.distances[stop_id][end_stop_id] for stop_id in start_stop_ids]
            meeting_metrics.append((end_stop_id, metric(distances_to_destination)))
        meeting_metrics.sort(key=lambda x: x[1])
        meeting_points = [stop_data(m[0], self.stops_df) for m in meeting_metrics]
        return MeetingResults(query.query_id, ErrorCodes.OK.value, meeting_points)
