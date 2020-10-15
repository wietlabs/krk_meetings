from functools import reduce
from src.data_provider.Extractor import Extractor

import pandas as pd
import numpy as np
import networkx as nx
from src.config import FLOYD_EXTRACTOR_PERIOD_MULTIPLIER, WALKING_ROUTE_ID


class FloydDataExtractor(Extractor):
    # @staticmethod
    # def add_walking_edges_to_floyd_graph(graph: nx.DiGraph, adjacent_stops: dict,
    #                                      kernelized: bool = False) -> nx.DiGraph:
    #     def edge_generator():
    #         for first, second in adjacent_stops:
    #             if first != second and (not kernelized or (graph.nodes[first]['hub'] and graph.nodes[second]['hub'])):
    #                 yield int(first), int(second), \
    #                       {'weight': int(adjacent_stops[first, second]), 'route_ids': WALKING_ROUTE_ID,
    #                        'path': [first, second]}
    #
    #     graph.add_edges_from(edge_generator())
    #     return graph

    # @staticmethod
    # def apply_adjacent_stops_to_hub_in_stops_df(graph_with_walking_edges: nx.DiGraph,
    #                                             stops_df: pd.DataFrame) -> pd.DataFrame:
    #     def is_hub(row):
    #         neighbour_count = len(list(graph_with_walking_edges.neighbors(row['stop_id'])))
    #         if row['is_first'] and row['is_last']:
    #             return neighbour_count > 1
    #         else:
    #             return neighbour_count > 2
    #
    #     stops_df = stops_df.reset_index()
    #     stops_df['hub'] = stops_df.apply(is_hub, axis=1)
    #     stops_df = stops_df.set_index('stop_id')
    #     return stops_df

    @staticmethod
    def create_kernelized_floyd_graph(graph: nx.DiGraph, stops_df: pd.DataFrame) -> nx.DiGraph:
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

    @staticmethod
    def get_distances(floyd_graph: nx.DiGraph) -> dict:
        distances = nx.floyd_warshall(floyd_graph)
        for key in distances.keys():
            distances[key] = dict(distances[key])
        return distances

    def create_floyd_graph(self, extended_transfers_df: pd.DataFrame, stops_df: pd.DataFrame) -> nx.DiGraph:
        def node_generator():
            for index, row in stops_df.iterrows():
                yield index, {'stop_name': row['stop_name'], 'stop_lat': row['stop_lat'],
                              'stop_lon': row['stop_lon'], 'hub': row['hub']}

        def edge_generator():
            for _, row in extended_transfers_df.iterrows():
                yield int(row['start_stop_id']), int(row['end_stop_id']), \
                      {'weight': int(row['duration'] + row['period'] * FLOYD_EXTRACTOR_PERIOD_MULTIPLIER),
                       'route_ids': row['route_id'], 'path': row['path']}

        floyd_graph = nx.DiGraph()
        floyd_graph.add_nodes_from(node_generator())
        floyd_graph.add_edges_from(edge_generator())

        return floyd_graph

    @staticmethod
    def create_floyd_transfers_df(extended_graph: nx.MultiDiGraph, adjacent_stops: dict) -> pd.DataFrame:
        graph = extended_graph

        def generator():
            for start_stop, end_stop, route_id in graph.edges(keys=True):
                duration = graph.edges[start_stop, end_stop, route_id]['duration']
                period = graph.edges[start_stop, end_stop, route_id]['period']
                path = graph.edges[start_stop, end_stop, route_id]['path']
                yield start_stop, end_stop, int(route_id), int(duration), int(period), tuple(path)
            for start_stop, end_stop in adjacent_stops:
                yield start_stop, end_stop, WALKING_ROUTE_ID, adjacent_stops[(start_stop, end_stop)], 0, (start_stop, end_stop)

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

    def get_next_stop(self, G: nx.MultiDiGraph, node_id: int, route_id: int, already_visited: list) -> tuple:
        for neighbour_id in G.neighbors(node_id):
            if neighbour_id not in already_visited:
                edge = G.get_edge_data(node_id, neighbour_id, route_id)
                if edge is not None:
                    return edge['route_id'], node_id, neighbour_id, edge['duration'], edge['period']
        return None

    def get_edges_data_from(self, graph: nx.MultiDiGraph, node_from_id: int, route_id: int) -> list:
        edges = set()
        for node_to_id in graph.neighbors(node_from_id):
            for edge in graph.get_edge_data(node_from_id, node_to_id).values():
                if edge['route_id'] == route_id:
                    edges.add(
                        (int(edge['route_id']), node_from_id, node_to_id, int(edge['duration']), int(edge['period'])))
        return list(edges)

    def generate_nodes(self, graph, stops_df) -> None:
        def node_generator():
            for stop_id, row in stops_df.iterrows():
                yield stop_id, {'stop_name': row['stop_name'], 'stop_lat': row['stop_lat'],
                                'stop_lon': row['stop_lon']}

        graph.add_nodes_from(node_generator())

    def generate_edges(self, graph, transfers_df, period_df) -> None:
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

        graph.add_edges_from(edge_generator())
