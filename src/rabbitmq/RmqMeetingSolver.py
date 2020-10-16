from src.exchanges import EXCHANGES
from src.data_classes.MeetingQuery import MeetingQuery
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.solver.MeetingSolver import MeetingSolver


def start_meeting_solver():
    meeting_solver = RmqMeetingSolver()
    meeting_solver.start()


class RmqMeetingSolver:
    def __init__(self):
        self.meeting_solver = MeetingSolver()
        self.query_consumer = RmqConsumer(EXCHANGES.MEETING_QUERY.value, self.consume_query)
        self.results_producer = RmqProducer(EXCHANGES.MEETING_RESULTS.value)

    def start(self):
        print("MeetingSolver: started.")
        self.query_consumer.start()

    def stop(self):
        self.query_consumer.stop()
        self.results_producer.stop()
        self.meeting_solver.data_manager.stop()

    def consume_query(self, query: MeetingQuery):
        meeting = self.meeting_solver.find_meeting_points(query)
        self.results_producer.send_msg(meeting, query.query_id)


if __name__ == "__main__":
    start_meeting_solver()
