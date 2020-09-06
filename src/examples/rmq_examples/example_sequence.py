from src.config import EXCHANGES
from src.data_classes.SequenceQuery import SequenceQuery
from src.data_classes.SequenceResults import SequenceResults
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer


class MockedApi:
    def __init__(self):
        self.results_consumer = RmqConsumer(EXCHANGES.SEQUENCE_RESULTS.value, print_sequence)
        self.query_producer = RmqProducer(EXCHANGES.SEQUENCE_QUERY.value)

    def start(self):
        self.results_consumer.start()

    def stop(self):
        self.results_consumer.stop()
        self.query_producer.stop()


def print_sequence(sequence: SequenceResults):
    print(sequence.best_sequence)


if __name__ == "__main__":
    mocked_api = MockedApi()

    stops_to_visit = ['Biprostal', 'Kawiory', 'Czarnowiejska']
    start_stop_name = 'Wrocławska'
    end_stop_name = 'AGH / UR'
    query = SequenceQuery(start_stop_name, end_stop_name, stops_to_visit)

    mocked_api.query_producer.send_msg(query)
    mocked_api.start()
