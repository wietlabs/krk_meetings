from src.config import EXCHANGES
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer


class MockedApi:
    def __init__(self):
        self.results_consumer = RmqConsumer(EXCHANGES.MEETING_RESULTS.value, print_meeting_points)
        self.query_producer = RmqProducer(EXCHANGES.MEETING_QUERY.value)

    def start(self):
        self.results_consumer.start()

    def stop(self):
        self.results_consumer.stop()
        self.query_producer.stop()


def print_meeting_points(meeting: MeetingResults):
    print(meeting.meeting_points)


if __name__ == "__main__":
    mocked_api = MockedApi()

    start_stop_names = ['Azory', 'Kawiory', 'Rondo Mogilskie']
    query = MeetingQuery(start_stop_names, 'square')

    mocked_api.query_producer.send_msg(query)
    mocked_api.start()
