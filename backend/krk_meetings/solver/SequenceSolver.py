from copy import copy

from krk_meetings.config import ErrorCodes, FloydDataPaths
from krk_meetings.data_classes.SequenceQuery import SequenceQuery
from krk_meetings.data_classes.SequenceResults import SequenceResults
from krk_meetings.solver import solver_utils
from krk_meetings.solver.interfaces.ISequenceSolver import ISequenceSolver
from krk_meetings.data_managers.SequenceDataManager import SequenceDataManager
from krk_meetings.logger import get_logger

logger = get_logger(__name__)


class SequenceSolver(ISequenceSolver):
    def __init__(self, data_path=FloydDataPaths):
        self.data_manager = SequenceDataManager(data_path)
        self.distances = None
        self.stops_df = None
        self.stops_df_by_name = None
        self.last_data_update = None

    def start(self):
        self.data_manager.start()
        if self.data_is_loaded():
            self.update_data()
        logger.info(f"SequenceSolver({id(self)}): started.")

    def data_is_loaded(self):
        if self.data_manager.data_loaded:
            return True
        else:
            logger.warn(f"SequenceSolver({id(self)}): Some pickles in data directory are missing this service won't "
                        f"work without them. Wait for DataProvider to finish processing GTFS files.")
            return False

    def update_data(self):
        data = self.data_manager.get_updated_data()
        self.distances = data["distances"]
        self.stops_df = data["stops_df"]
        self.stops_df_by_name = data["stops_df_by_name"]
        self.last_data_update = self.data_manager.last_data_update

    def find_best_sequence(self, query: SequenceQuery) -> SequenceResults:
        logger.info(f"SequenceSolver({id(self)}): finding best sequence.")
        if not self.data_is_loaded():
            return SequenceResults(query.query_id, ErrorCodes.INTERNAL_DATA_NOT_LOADED.value, [])
        if self.last_data_update is None or self.last_data_update < self.data_manager.last_data_update:
            self.update_data()

        def gen(stop_ids: list, current_stop_id, last_stop_id, sequence: list, weight: int):
            if stop_ids:
                for next_stop_id in stop_ids:
                    next_stop_ids = copy(stop_ids)
                    next_stop_ids.remove(next_stop_id)
                    next_sequence = copy(sequence)
                    next_sequence.append(next_stop_id)
                    next_weight = weight + self.distances[current_stop_id][next_stop_id]
                    yield from gen(next_stop_ids, next_stop_id, last_stop_id, next_sequence, next_weight)
            else:
                sequence.append(last_stop_id)
                weight = weight + self.distances[current_stop_id][last_stop_id]
                yield sequence, weight


        start_stop_id = solver_utils.get_stop_id_by_name(query.start_stop_name, self.stops_df_by_name)
        if start_stop_id is None:
            return SequenceResults(query.query_id, ErrorCodes.BAD_START_STOP_NAME.value, [])
        end_stop_id = solver_utils.get_stop_id_by_name(query.end_stop_name, self.stops_df_by_name)
        if start_stop_id is None:
            return SequenceResults(query.query_id, ErrorCodes.BAD_END_STOP_NAME.value, [])
        stops_to_visit_ids = [solver_utils.get_stop_id_by_name(stop_name, self.stops_df_by_name) for stop_name in query.stops_to_visit]
        if None in stops_to_visit_ids:
            return SequenceResults(query.query_id, ErrorCodes.BAD_STOP_NAMES_IN_SEQUENCE.value, [])

        sequences = list(gen(stops_to_visit_ids, start_stop_id, end_stop_id, [start_stop_id], 0))
        best_sequence = min(sequences, key=lambda x: x[1])
        best_sequence = list(map(lambda x: self.stops_df.at[x, 'stop_name'], best_sequence[0]))
        return SequenceResults(query.query_id, ErrorCodes.OK.value, best_sequence)
