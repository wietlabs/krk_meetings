import json

from src.config import EXCHANGES
from src.data_classes.SequenceResults import SequenceResults
from src.rabbitmq.RmqConsumer import RmqOneMsgConsumer
from src.rabbitmq.RmqProducer import RmqProducer


class MockedApi:
    def __init__(self, task_id):
        self.results_consumer = RmqOneMsgConsumer(EXCHANGES.SEQUENCE_RESULTS.value, task_id)
        self.query_producer = RmqProducer(EXCHANGES.SEQUENCE_QUERY.value)

    def receive_msg(self):
        return self.results_consumer.receive_msg()

    def stop(self):
        self.query_producer.stop()
        del self.results_consumer
        del self.query_producer


def print_sequence(sequence):
    sequence = SequenceResults.from_json(json.dumps(sequence))
    print(sequence.best_sequence)


if __name__ == "__main__":
    task_id = 1
    mocked_api = MockedApi(task_id)
    query_json = {
        "query_id": task_id,
        "start_stop_name": "Wrocławska",
        "end_stop_name": "AGH / UR",
        "stops_to_visit": ["Biprostal", "Kawiory", "Rondo Mogilskie", "Czarnowiejska"]
    }
    mocked_api.query_producer.send_msg(query_json)
    print_sequence(mocked_api.receive_msg())
    mocked_api.stop()
