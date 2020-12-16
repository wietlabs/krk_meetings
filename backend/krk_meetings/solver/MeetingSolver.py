from krk_meetings.config import ErrorCodes, FloydDataPaths
from krk_meetings.data_classes.MeetingQuery import MeetingQuery
from krk_meetings.data_classes.MeetingResults import MeetingResults
from krk_meetings.solver import solver_utils
from krk_meetings.solver.interfaces.IMeetingSolver import IMeetingSolver
from krk_meetings.data_managers.MeetingDataManager import MeetingDataManager
from krk_meetings.solver.solver_utils import meeting_stop_data
from krk_meetings.logger import get_logger

logger = get_logger(__name__)


class MeetingSolver(IMeetingSolver):
    def __init__(self, data_path=FloydDataPaths):
        self.data_manager = MeetingDataManager(data_path)
        self.distances = None
        self.stops_df = None
        self.stops_df_by_name = None
        self.last_data_update = None

    def start(self):
        self.data_manager.start()
        self.update_data()
        logger.info(f"MeetingSolver({id(self)}): started.")

    def update_data(self):
        data = self.data_manager.get_updated_data()
        self.distances = data["distances"]
        self.stops_df = data["stops_df"]
        self.stops_df_by_name = data["stops_df_by_name"]
        self.last_data_update = self.data_manager.last_data_update

    def find_meeting_points(self, query: MeetingQuery) -> MeetingResults:
        logger.info(f"MeetingSolver({id(self)}): finding meeting points.")
        if self.last_data_update is None or self.last_data_update < self.data_manager.last_data_update:
            self.update_data()
        start_stop_ids = [solver_utils.get_stop_id_by_name(stop_name, self.stops_df_by_name) for stop_name in query.start_stop_names]
        if None in start_stop_ids:
            return MeetingResults(query.query_id, ErrorCodes.BAD_STOP_NAMES_IN_SEQUENCE.value, [])

        if query.norm == 'square':
            norm = lambda l: sum(map(lambda i: i * i, l))
        elif query.norm == 'sum':
            norm = lambda l: sum(l)
        elif query.norm == 'max':
            norm = lambda l: max(l)
        else:
            return None

        meeting_norms = []
        for end_stop_id in self.distances:
            distances_to_destination = [self.distances[stop_id][end_stop_id] for stop_id in start_stop_ids]
            meeting_norms.append((end_stop_id, norm(distances_to_destination)))
        meeting_norms.sort(key=lambda x: x[1])
        meeting_points = [meeting_stop_data(norm, self.stops_df) for norm in meeting_norms[0:10]]
        return MeetingResults(query.query_id, ErrorCodes.OK.value, meeting_points)
