from datetime import date, time

from src.config import EXCHANGES
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer


class MockedApi:
    def __init__(self):
        self.results_consumer = RmqConsumer(EXCHANGES.CONNECTION_RESULTS.value, print_connections)
        self.query_producer = RmqProducer(EXCHANGES.CONNECTION_QUERY.value)

    def start(self):
        self.results_consumer.start()

    def stop(self):
        self.results_consumer.stop()
        self.query_producer.stop()


def print_connections(connections):
    for connection in connections:
        print(connection)
        print('-' * 30)


if __name__ == "__main__":
    mocked_api = MockedApi()

    start_date = date(2020, 5, 24)
    start_time = time(20, 0, 0)
    start_stop_name = 'Teatr Słowackiego'
    end_stop_name = 'Kurdwanów P+R'
    query = ConnectionQuery(start_date, start_time, start_stop_name, end_stop_name)

    mocked_api.query_producer.send_msg(query)
    mocked_api.start()
