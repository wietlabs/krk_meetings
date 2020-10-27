from copy import copy
from src.data_classes.SequenceQuery import SequenceQuery
from src.data_classes.SequenceResults import SequenceResults
from src.solver.ISequenceSolver import ISequenceSolver
from src.data_managers.SequenceDataManager import SequenceDataManager


class SequenceSolver(ISequenceSolver):
    def __init__(self, ):
        self.data_manager = SequenceDataManager()
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

    def find_best_sequence(self, query: SequenceQuery) -> SequenceResults:
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

        stops_to_visit_ids = list(map(lambda x: int(self.stops_df_by_name.at[x, 'stop_id']), query.stops_to_visit))
        start_stop_id = int(self.stops_df_by_name.at[query.start_stop_name, 'stop_id'])
        end_stop_id = int(self.stops_df_by_name.at[query.end_stop_name, 'stop_id'])
        sequences = list(gen(stops_to_visit_ids, start_stop_id, end_stop_id, [start_stop_id], 0))
        best_sequence = min(sequences, key=lambda x: x[1])
        best_sequence = list(map(lambda x: self.stops_df.at[x, 'stop_name'], best_sequence[0]))
        return SequenceResults(query.query_id, best_sequence)
