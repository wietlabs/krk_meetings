from copy import copy
from time import sleep

from src.data_classes.SequenceQuery import SequenceQuery
from src.data_classes.SequenceResults import SequenceResults
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.solver.DataUpdater import DataUpdater
from src.solver.ISequenceSolver import ISequenceSolver

from src.exchanges import EXCHANGES


def start_sequence_solver():
    sequence_solver = SequenceSolver()
    sequence_solver.start()


class SequenceSolver(DataUpdater, ISequenceSolver):
    def __init__(self):
        DataUpdater.__init__(self)
        self.query_consumer = RmqConsumer(EXCHANGES.SEQUENCE_QUERY.value, self.consume_sequence_query)
        self.results_producer = RmqProducer(EXCHANGES.SEQUENCE_RESULTS.value)

    def start(self):
        DataUpdater.start(self)
        print("SequenceSolver: started.")
        self.query_consumer.start()

    def stop(self):
        DataUpdater.stop(self)
        self.query_consumer.stop()
        self.results_producer.stop()

    def consume_sequence_query(self, query: SequenceQuery):
        with self.lock:
            best_sequence = self.find_best_sequence(query)
        sleep(0.001)
        self.results_producer.send_msg(best_sequence, query.query_id)

    def find_best_sequence(self, query: SequenceQuery) -> SequenceResults:
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
        return SequenceResults(best_sequence)
