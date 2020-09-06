from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.solver.DataUpdater import DataUpdater
from src.solver.IMeetingSolver import IMeetingSolver

from src.config import EXCHANGES


def start_meeting_solver():
    meeting_solver = MeetingSolver()
    meeting_solver.start()


class MeetingSolver(DataUpdater, IMeetingSolver):
    def __init__(self):
        DataUpdater.__init__(self)
        self.query_consumer = RmqConsumer(EXCHANGES.MEETING_QUERY.value, self.consume_meeting_query)
        self.results_producer = RmqProducer(EXCHANGES.MEETING_RESULTS.value)

    def start(self):
        DataUpdater.start(self)
        print("MeetingSolver has started.")
        self.query_consumer.start()

    def stop(self):
        DataUpdater.stop(self)
        self.query_consumer.stop()
        self.results_producer.stop()

    def consume_meeting_query(self, query: MeetingQuery):
        with self.lock:
            meeting_points = self.find_meeting_points(query)
            self.results_producer.send_msg(meeting_points)

    def find_meeting_points(self, query: MeetingQuery) -> MeetingResults:
        start_stop_ids = list(map(lambda x: int(self.stops_df_by_name.at[x, 'stop_id']), query.start_stop_names))
        if query.metric == 'square':
            metric = lambda l: sum(map(lambda i: i * i, l))
        elif query.metric == 'sum':
            metric = lambda l: sum(l)
        elif query.metric == 'max':
            metric = lambda l: max(l)
        else:
            return None
        meeting_metrics = []
        for end_stop_id in self.distances:
            distances_to_destination = list(map(lambda stop_id: self.distances[stop_id][end_stop_id], start_stop_ids))
            meeting_metrics.append((end_stop_id, metric(distances_to_destination)))
        meeting_metrics.sort(key=lambda x: x[1])
        meeting_points = list(map(lambda x: self.stops_df.at[x[0], 'stop_name'], meeting_metrics[0:10]))
        return MeetingResults(meeting_points)
