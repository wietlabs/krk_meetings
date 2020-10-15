import json

from src.config import EXCHANGES
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.rabbitmq.RmqConsumer import RmqConsumer, RmqOneMsgConsumer
from src.rabbitmq.RmqProducer import RmqProducer


class MockedApi:
    def __init__(self, task_id):
        self.results_consumer = RmqOneMsgConsumer(EXCHANGES.MEETING_RESULTS.value, task_id)
        self.query_producer = RmqProducer(EXCHANGES.MEETING_QUERY.value)

    def receive_msg(self):
        return self.results_consumer.receive_msg()

    def stop(self):
        self.query_producer.stop()
        del self.results_consumer
        del self.query_producer


def print_meeting_points(meeting):
    meeting = MeetingResults.from_json(json.dumps(meeting))
    print(meeting.meeting_points)


if __name__ == "__main__":
    task_id = 1
    mocked_api = MockedApi(task_id)
    query_json = {
        "query_id": task_id,
        "start_stop_names": ["Azory", "Kawiory", "Rondo Mogilskie"],
        "metric": "square"
    }
    mocked_api.query_producer.send_msg(query_json)
    print_meeting_points(mocked_api.receive_msg())
    mocked_api.stop()

