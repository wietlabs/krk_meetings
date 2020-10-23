import json
from datetime import date, time

from src.config import EXCHANGES
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_classes.Connection import Connection
from src.rabbitmq.RmqConsumer import RmqConsumer, RmqOneMsgConsumer
from src.rabbitmq.RmqProducer import RmqProducer


class MockedApi:
    def __init__(self, task_id):
        self.results_consumer = RmqOneMsgConsumer(EXCHANGES.FLASK_SERVER.value, task_id)
        self.query_producer = RmqProducer(EXCHANGES.CONNECTION_QUERY.value)

    def receive_msg(self):
        return self.results_consumer.receive_msg()

    def stop(self):
        self.query_producer.stop()
        del self.results_consumer
        del self.query_producer


def print_connections(connections):
    connections = Connections.from_json(json.dumps(connections))
    for connection in connections:
        print(connection)
        print('-' * 30)


if __name__ == "__main__":
    task_id = 1
    mocked_api = MockedApi(task_id)
    query_json = {
        "query_id": task_id,
        "start_date": "2020-5-24",
        "start_time": "20:00:00",
        "start_stop_id": 1,
        "end_stop_id": 2
    }
    mocked_api.query_producer.send_msg(query_json)
    print_connections(mocked_api.receive_msg())
    mocked_api.stop()

