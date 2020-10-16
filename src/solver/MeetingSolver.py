from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.solver.IMeetingSolver import IMeetingSolver
from src.solver.DataManager import DataManager


class MeetingSolver(IMeetingSolver):
    def __init__(self, ):
        self.data_manager = DataManager()
        self.graph = None
        self.kernelized_graph = None
        self.distances = None
        self.stops_df = None
        self.routes_df = None
        self.stops_df_by_name = None
        self.stop_times_0 = None
        self.stop_times_24 = None
        self.paths = None
        self.day_to_services_dict = None
        self.adjacent_stops = None

        self.data_manager.start()
        self.data_manager.update_data()
        self.update_data()

    def update_data(self):
        if not self.data_manager.up_to_date:
            data = self.data_manager.get_updated_data()
            self.graph = data.graph
            self.kernelized_graph = data.kernelized_graph
            self.distances = data.distances_dict
            self.stops_df = data.stops_df
            self.routes_df = data.routes_df
            self.stops_df_by_name = data.stops_df_by_name
            self.stop_times_0 = data.stop_times_0_dict
            self.stop_times_24 = data.stop_times_24_dict
            self.day_to_services_dict = data.day_to_services_dict
            self.adjacent_stops = data.adjacent_stops
            self.paths = dict()
            for node in self.graph.nodes():
                self.paths[node] = dict()

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
