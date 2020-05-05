import networkx as nx

from solvers.ISolver import ISolver
from solvers.Query import Query
from static_timetable_module.gtfs_static.ParsedData import ParsedData


class BasicSolver(ISolver):
    def __init__(self, parsed_data: ParsedData):
        # self.G = nx.read_gpickle('G.gpickle')
        # self.G_R = nx.read_gpickle('G_R.gpickle')
        # return

        G = nx.MultiDiGraph()  # or DiGraph

        stops_df = parsed_data.stops_df
        stop_times_df = parsed_data.stop_times_df
        transfers_df = parsed_data.transfers_df

        unique_stop_times_df = stop_times_df.reset_index()[['stop_id', 'departure_time']]
        unique_stop_times_df['dummy'] = None  # TODO: refactor to remove this dummy column
        unique_stop_times_df = unique_stop_times_df.groupby(['stop_id', 'departure_time']).first().sort_index()

        transfers_df = transfers_df[['start_time', 'end_time', 'start_stop_id', 'end_stop_id', 'duration']]

        G.add_nodes_from(
            (stop_id, time)
            for stop_id, time in unique_stop_times_df.index
        )

        G.add_weighted_edges_from(
            ((start_stop_id, start_time), (end_stop_id, end_time), duration)
            for _, (start_time, end_time, start_stop_id, end_stop_id, duration) in transfers_df.iterrows()
        )
        # TODO: include weekdays using service_id

        # trick #1: add destination nodes
        G.add_nodes_from(
            (stop_id, None)
            for stop_id in stops_df.index
        )

        # trick #2: merged waiting edges
        G.add_weighted_edges_from(
            ((stop_id, start_time), (stop_id, end_time), (end_time - start_time) % (24 * 60 * 60))
            for stop_id, df in unique_stop_times_df.groupby('stop_id')
            for (_, start_time), (_, end_time) in nx.utils.pairwise(df.index, cyclic=True)
        )

        # trick #3: use reversed graph to find the latest departure time
        G_R = G.reverse()

        G.add_edges_from((
            ((stop_id, time), (stop_id, None))
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        G_R.add_edges_from((
            ((stop_id, time), (stop_id, None))
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        nx.write_gpickle(G, 'G.gpickle')
        nx.write_gpickle(G_R, 'G_R.gpickle')

        self.G = G
        self.G_R = G_R

    def find_connection(self, query: Query):
        start_time = query.start_time
        start_stop_id = query.start_stop_id
        end_stop_id = query.end_stop_id

        start_node = (start_stop_id, start_time)  # TODO: find first existing start node
        end_node = (end_stop_id, None)

        # shortest_path = nx.shortest_path(self.G, start_node, end_node)
        # return shortest_path

        shortest_path_length = nx.shortest_path_length(self.G, start_node, end_node, 'weight')

        start_node = (end_stop_id, (start_time + shortest_path_length) % (24 * 60 * 60))
        end_node = (start_stop_id, None)

        shortest_path_inverted = nx.shortest_path(self.G_R, start_node, end_node, 'weight')

        shortest_path = shortest_path_inverted[:-1][::-1]
        return shortest_path
