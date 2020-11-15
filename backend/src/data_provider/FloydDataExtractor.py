from functools import reduce
from src.data_provider.Extractor import Extractor
import pandas as pd
import networkx as nx
from src.config import DEFAULT_FLOYD_EXTRACTOR_CONFIGURATION
from src.data_provider.utils import is_nightly


class FloydDataExtractor(Extractor):
    def __init__(self, configuration=DEFAULT_FLOYD_EXTRACTOR_CONFIGURATION):
        super().__init__()
        self.configuration=configuration

    @staticmethod
    def create_kernelized_floyd_graph(graph: nx.DiGraph, stops_df: pd.DataFrame) -> nx.DiGraph:
        kernelized_graph = nx.DiGraph()
        stops_df = stops_df[stops_df['hub']]

        def node_generator():
            for stop_id, stop_name, stop_lat, stop_lon, is_first, is_last, hub in stops_df.itertuples():
                yield stop_id, {'stop_name': stop_name, 'stop_lat': stop_lat, 'stop_lon': stop_lon, 'hub': hub}

        def edge_generator():
            for first, second in graph.edges:
                if graph.nodes[first]['hub'] and graph.nodes[second]['hub']:
                    attr = graph.edges[first, second]
                    yield first, second, attr

        kernelized_graph.add_nodes_from(node_generator())
        kernelized_graph.add_edges_from(edge_generator())
        return kernelized_graph

    @staticmethod
    def get_distances(floyd_graph: nx.DiGraph) -> dict:
        distances = nx.floyd_warshall(floyd_graph)
        for key in distances.keys():
            distances[key] = dict(distances[key])
        return distances

    def create_floyd_graph(self, extended_transfers_df: pd.DataFrame, stops_df: pd.DataFrame) -> nx.DiGraph:
        def node_generator():
            for stop_id, stop_name, stop_lat, stop_lon, is_first, is_last, hub in stops_df.itertuples():
                yield stop_id, {'stop_name': stop_name, 'stop_lat': stop_lat, 'stop_lon': stop_lon, 'hub': hub}

        def edge_generator():
            for _, start_stop_id, end_stop_id, path, duration, period, route_id in extended_transfers_df.itertuples():
                weight = int(duration + period + self.configuration.change_penalty)
                yield int(start_stop_id), int(end_stop_id), {'weight': weight, 'route_ids': route_id, 'path': path}

        floyd_graph = nx.DiGraph()
        floyd_graph.add_nodes_from(node_generator())
        floyd_graph.add_edges_from(edge_generator())

        return floyd_graph

    def create_floyd_transfers_df(self, extended_graph: nx.MultiDiGraph, adjacent_stops: dict) -> pd.DataFrame:
        graph = extended_graph

        def generator():
            for start_stop, end_stop, route_id in graph.edges(keys=True):
                duration = graph.edges[start_stop, end_stop, route_id]['duration']
                period = graph.edges[start_stop, end_stop, route_id]['period']
                path = graph.edges[start_stop, end_stop, route_id]['path']
                yield start_stop, end_stop, int(route_id), int(duration), int(period), tuple(path)
            for start_stop, end_stop in adjacent_stops:
                yield start_stop, end_stop, self.configuration.walking_route_id,\
                      adjacent_stops[(start_stop, end_stop)], 0, (start_stop, end_stop)

        df = pd.DataFrame(generator(),
                          columns=['start_stop_id', 'end_stop_id', 'route_id', 'duration', 'period', 'path'])
        df = df.astype(dtype={'start_stop_id': 'int64', 'end_stop_id': 'int64', 'route_id': 'int64',
                              'duration': 'int64', 'period': 'int64', 'path': 'object'})

        def harmonic_sum(series):
            return int(reduce(lambda x, y: (x * y) / (x + y), series))

        def set_walking_duration(row):
            if (row['start_stop_id'], row['end_stop_id']) in adjacent_stops:
                return adjacent_stops[(row['start_stop_id'], row['end_stop_id'])]
            else:
                return row['duration']

        def set_walking_period(row):
            if (row['start_stop_id'], row['end_stop_id']) in adjacent_stops:
                return 0
            else:
                return row['period']

        df = df.groupby(['start_stop_id', 'end_stop_id', 'path']) \
            .agg({'duration': 'mean', 'period': harmonic_sum, 'route_id': lambda r: tuple(r)})

        df = df.reset_index()
        df['duration'] = df.apply(set_walking_duration, axis=1)
        df['period'] = df.apply(set_walking_period, axis=1)

        return df

    @staticmethod
    def transform_stop_times_df_to_dict(stops_df, stop_times_df, services_list) -> dict:
        stop_times_dict = dict()
        stop_ids = stops_df.index.tolist()
        for stop_id in stop_ids:
            times_by_stop_0 = stop_times_df[stop_times_df['stop_id'] == stop_id]
            stop_times_dict[stop_id] = {}
            for service in services_list:
                stop_times_dict[stop_id][service] = times_by_stop_0[times_by_stop_0['service'] == service] \
                    [['departure_time', 'route_id']]
        return stop_times_dict

    def extract_graph(self, stops_df: pd.DataFrame, transfers_df: pd.DataFrame,
                      period_df: pd.DataFrame) -> nx.MultiDiGraph:
        graph = nx.MultiDiGraph()
        self.generate_nodes(graph, stops_df)
        self.generate_edges(graph, transfers_df, period_df)
        return graph

    def extend_graph(self, graph: nx.MultiDiGraph, stops_df: pd.DataFrame) -> nx.MultiDiGraph:
        first_stops = stops_df[['is_first']].reset_index('stop_id')
        first_stops = list(first_stops.drop_duplicates('stop_id')['stop_id'])
        start_routes = {}
        for first, second, route in graph.edges:
            if first not in start_routes:
                start_routes[first] = set()
            start_routes[first].add(route)

        for start_node in first_stops:
            if start_node not in start_routes:
                # TODO temporary fix, nodes with names PH and PT aren't in the dict
                continue
            for route_id in start_routes[start_node]:
                edges = self.get_edges_data_from(graph, start_node, route_id)
                for edge in edges:
                    _, _, first_neighbour, first_duration, period = edge
                    graph.add_edges_from(self.extended_edges_generator(
                        graph, start_node, first_neighbour, first_duration, route_id, period))
        return graph

    def extended_edges_generator(self, graph, start_node, first_neighbour, first_duration, route_id, period) -> None:
        edges = [(start_node, first_neighbour, first_duration)]
        already_visited = [start_node, first_neighbour]
        current_node = first_neighbour
        while True:
            next_edge = self.get_next_stop(graph, current_node, route_id, already_visited)
            if next_edge is None:
                break
            _, _, next_node, duration, _ = next_edge
            # TODO Why it occures?
            if duration > 3600:
                break

            edges.append((current_node, next_node, duration))
            already_visited.append(next_node)
            current_node = next_node

        for first_index in range(len(edges)):
            first_node, _, current_duration = edges[first_index]
            path = []
            for last_index in range(first_index + 1, len(edges)):
                node_from, node_to, duration = edges[last_index]
                current_duration += duration
                path.append(node_from)
                yield first_node, node_to, route_id, {
                    'duration': current_duration,
                    'period': period,
                    'route_id': route_id,
                    'path': path
                }

    @staticmethod
    def get_next_stop(graph: nx.MultiDiGraph, node_id: int, route_id: int, already_visited: list) -> tuple:
        for neighbour_id in graph.neighbors(node_id):
            if neighbour_id not in already_visited:
                edge = graph.get_edge_data(node_id, neighbour_id, route_id)
                if edge is not None:
                    return edge['route_id'], node_id, neighbour_id, edge['duration'], edge['period']
        return None

    @staticmethod
    def get_edges_data_from(graph: nx.MultiDiGraph, node_from_id: int, route_id: int) -> list:
        edges = set()
        for node_to_id in graph.neighbors(node_from_id):
            for edge in graph.get_edge_data(node_from_id, node_to_id).values():
                if edge['route_id'] == route_id:
                    edges.add(
                        (int(edge['route_id']), node_from_id, node_to_id, int(edge['duration']), int(edge['period'])))
        return list(edges)

    @staticmethod
    def generate_nodes(graph: nx.MultiDiGraph, stops_df: pd.DataFrame) -> None:
        def node_generator():
            for stop_id, stop_name, stop_lat, stop_lon, _, _ in stops_df.itertuples():
                yield stop_id, {'stop_name': stop_name, 'stop_lat': stop_lat, 'stop_lon': stop_lon}

        graph.add_nodes_from(node_generator())

    @staticmethod
    def generate_edges(graph: nx.MultiDiGraph, transfers_df: pd.DataFrame, period_df: pd.DataFrame) -> None:
        transfers_df = transfers_df[[
            'route_id', 'start_stop_id', 'end_stop_id', 'duration']]
        avg_transfers_df = transfers_df.groupby(['route_id', 'start_stop_id', 'end_stop_id']).mean().reset_index()

        def edge_generator():
            for _, route_id, start_node, end_node, duration in avg_transfers_df.itertuples():
                period = period_df.at[(route_id, 'period')]
                yield start_node, int(end_node), int(route_id), \
                    {'route_id': int(route_id), 'duration': int(duration), 'period': int(period), 'path': []}

        graph.add_edges_from(edge_generator())

    def create_period_df(self, stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame, routes_df: pd.DataFrame
                         ) -> pd.DataFrame:
        stop_times_df = stop_times_df.reset_index()
        df = stop_times_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df = df[df['stop_sequence'] == 2]
        df = df[['route_id', 'departure_time']]
        df = df.groupby(['route_id']).agg({'departure_time': ['count', 'min', 'max']})
        df.columns = ['count', 'min', 'max']
        df = df.reset_index()
        df['period'] = df.apply(lambda row: self.get_period(row['route_id'], row['count'], routes_df), axis=1)
        df = df.reset_index()
        df = df[['route_id', 'period']]
        df = df.set_index('route_id')
        return df

    def get_period(self, route_id, count, routes_df: pd.DataFrame):
        nightly = is_nightly(routes_df.at[route_id, 'route_name'], self.configuration.nightly_route_ranges)
        if nightly:
            running_hours = self.configuration.nightly_hours
            multiplier = self.configuration.nightly_period_multiplier
        else:
            running_hours = self.configuration.daily_hours
            multiplier = self.configuration.daily_period_multiplier
        return int(running_hours * 3600 / count * self.configuration.number_of_services * multiplier)
