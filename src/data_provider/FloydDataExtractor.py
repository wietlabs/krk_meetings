from functools import reduce
from src.data_provider.Extractor import Extractor

import pandas as pd
import networkx as nx
from src.config import FLOYD_EXTRACTOR_PERIOD_MULTIPLIER


class FloydDataExtractor(Extractor):
    def create_kernelized_floyd_graph(self, graph: nx.DiGraph, stops_df):
        kernelized_graph = nx.DiGraph()
        stops_df = stops_df[stops_df['hub']]

        def node_generator():
            for index, row in stops_df.iterrows():
                yield index, {'stop_name': row['stop_name'], 'stop_lat': row['stop_lat'],
                              'stop_lon': row['stop_lon'], 'hub': row['hub']}

        def edge_generator():
            for first, second in graph.edges:
                if graph.nodes[first]['hub'] and graph.nodes[second]['hub']:
                    attr = graph.edges[first, second]
                    yield first, second, attr

        kernelized_graph.add_nodes_from(node_generator())
        kernelized_graph.add_edges_from(edge_generator())
        return kernelized_graph

    def get_distances(self, floyd_graph):
        distances = nx.floyd_warshall(floyd_graph)
        for key in distances.keys():
            distances[key] = dict(distances[key])
        return distances

    def create_floyd_graph(self, extended_transfers_df: pd.DataFrame, stops_df: pd.DataFrame):
        def harmonic_sum(series):
            return int(reduce(lambda x, y: (x * y) / (x + y), series))

        extended_transfers_df = extended_transfers_df.groupby(['start_stop_id', 'end_stop_id', 'path']) \
            .agg({'duration': 'mean', 'period': harmonic_sum, 'route_id': lambda r: tuple(r)})
        extended_transfers_df = extended_transfers_df.reset_index()

        floyd_graph = nx.DiGraph()
        self.generate_floyd_nodes(floyd_graph, stops_df)
        self.generate_floyd_edges(floyd_graph, extended_transfers_df)

        return floyd_graph

    def generate_floyd_nodes(self, graph, stops_df):
        stops_df = stops_df.reset_index()

        def node_generator():
            for _, row in stops_df.iterrows():
                yield row['stop_id'], {'stop_name': row['stop_name'], 'stop_lat': row['stop_lat'],
                                       'stop_lon': row['stop_lon'], 'hub': row['hub']}

        graph.add_nodes_from(node_generator())

    def generate_floyd_edges(self, graph, transfers_df):
        def edge_generator():
            for _, row in transfers_df.iterrows():
                yield int(row['start_stop_id']), int(row['end_stop_id']), \
                      {'weight': int(row['duration'] + row['period'] * FLOYD_EXTRACTOR_PERIOD_MULTIPLIER),
                       'route_ids': row['route_id'], 'path': row['path']}

        graph.add_edges_from(edge_generator())

    def create_extended_transfers_df(self, extended_graph: nx.MultiDiGraph):
        graph = extended_graph

        def generator():
            for strat_stop, end_stop, route_id in graph.edges(keys=True):
                duration = graph.edges[strat_stop, end_stop, route_id]['duration']
                period = graph.edges[strat_stop, end_stop, route_id]['period']
                path = graph.edges[strat_stop, end_stop, route_id]['path']
                yield strat_stop, end_stop, int(route_id), int(duration), int(period), tuple(path)

        df = pd.DataFrame(generator(),
                          columns=['start_stop_id', 'end_stop_id', 'route_id', 'duration', 'period', 'path'])
        df = df.astype(dtype={'start_stop_id': 'int64', 'end_stop_id': 'int64', 'route_id': 'int64',
                              'duration': 'int64', 'period': 'int64', 'path': 'object'})
        return df

    def transform_stop_times_df_to_dict(self, stops_df, stop_times_df, services_list):
        stop_times_dict = dict()
        stop_ids = stops_df.index.tolist()
        for stop_id in stop_ids:
            times_by_stop_0 = stop_times_df[stop_times_df['stop_id'] == stop_id]
            for service in services_list:
                stop_times_dict[(service, stop_id)] = times_by_stop_0[times_by_stop_0['service'] == service] \
                    [['departure_time']]
        return stop_times_dict

    def extract_graph(self, stops_df: pd.DataFrame, transfers_df: pd.DataFrame, period_df: pd.DataFrame):
        G = nx.MultiDiGraph()
        self.generate_nodes(G, stops_df)
        self.generate_edges(G, transfers_df, period_df)
        return G

    def extend_graph(self, graph: nx.MultiDiGraph, stops_df: pd.DataFrame):
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

    def extended_edges_generator(self, G, start_node, first_neighbour, first_duration, route_id, period):
        edges = [(start_node, first_neighbour, first_duration)]
        already_visited = [start_node, first_neighbour]
        current_node = first_neighbour
        while True:
            next_edge = self.get_next_stop(G, current_node, route_id, already_visited)
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

    def get_next_stop(self, G: nx.MultiDiGraph, node_id: int, route_id: int, already_visited: list):
        for neighbour_id in G.neighbors(node_id):
            if neighbour_id not in already_visited:
                edge = G.get_edge_data(node_id, neighbour_id, route_id)
                if edge is not None:
                    return edge['route_id'], node_id, neighbour_id, edge['duration'], edge['period']
        return None

    def get_edges_data_from(self, G: nx.MultiDiGraph, node_from_id: int, route_id: int):
        edges = set()
        for node_to_id in G.neighbors(node_from_id):
            for edge in G.get_edge_data(node_from_id, node_to_id).values():
                if edge['route_id'] == route_id:
                    edges.add(
                        (int(edge['route_id']), node_from_id, node_to_id, int(edge['duration']), int(edge['period'])))
        return list(edges)

    def generate_nodes(self, G, stops_df):
        def node_generator():
            for stop_id, row in stops_df.iterrows():
                yield stop_id, {'stop_name': row['stop_name'], 'stop_lat': row['stop_lat'],
                                'stop_lon': row['stop_lon'], 'hub': row['hub']}

        G.add_nodes_from(node_generator())

    def generate_edges(self, G, transfers_df, period_df):
        transfers_df = transfers_df[[
            'route_id', 'start_stop_id', 'end_stop_id', 'duration']]
        avg_transfers_df = transfers_df.groupby(['route_id', 'start_stop_id', 'end_stop_id']).mean().reset_index()

        def edge_generator():
            for _, row in avg_transfers_df.iterrows():
                start_node = int(row['start_stop_id'])
                end_node = int(row['end_stop_id'])
                route_id = int(row['route_id'])
                duration = row['duration']
                period = int(period_df.at[(route_id, 'period')])
                yield start_node, end_node, route_id, \
                      {'route_id': route_id, 'duration': duration, 'period': period, 'path': []}

        G.add_edges_from(edge_generator())
