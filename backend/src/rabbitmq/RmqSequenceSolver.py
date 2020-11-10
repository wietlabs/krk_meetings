from src.exchanges import EXCHANGES
from src.data_classes.SequenceQuery import SequenceQuery
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.solver.SequenceSolver import SequenceSolver


def start_sequence_solver():
    sequence_solver = RmqSequenceSolver()
    sequence_solver.start()


class RmqSequenceSolver:
    def __init__(self):
        self.sequence_solver = SequenceSolver()
        self.query_consumer = RmqConsumer(EXCHANGES.SEQUENCE_QUERY.value, self.consume_query)
        self.results_producer = RmqProducer(EXCHANGES.FLASK_SERVER_SEQUENCE.value)

    def start(self):
        print("SequenceSolver: started.")
        self.query_consumer.start()

    def stop(self):
        self.query_consumer.stop()
        self.results_producer.stop()
        self.sequence_solver.data_manager.stop()

    def consume_query(self, query: SequenceQuery):
        sequence = self.sequence_solver.find_best_sequence(query)
        self.results_producer.send_msg(sequence)


if __name__ == "__main__":
    start_sequence_solver()
