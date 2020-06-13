from functools import reduce
from DataClasses.GraphData import GraphData

import pandas as pd
import networkx as nx

from DataClasses import ExtractedData
from config import PERIOD_MULTIPLIER


class GraphDataExtractor:
    def extract(self, extracted_data: ExtractedData):
        stops_df = extracted_data.stops_df
        transfers_df = extracted_data.transfers_df
        stop_times_df = extracted_data.stop_times_df
        first_stops_df = extracted_data.first_stops_df
        period_df = extracted_data.period_df
        routes_df = extracted_data.routes_df.set_index(['service_id', 'block_id', 'trip_num'])
        stops_df_by_name = extracted_data.stops_df_by_name

        # hubs_df = stops_df[stops_df['hub']]
        # hubs_df = hubs_df.reset_index()
        # hub_list = list(hubs_df['stop_id'].drop_duplicates())

        graph = self.extract_graph(stops_df, transfers_df, first_stops_df, period_df)

        # kernelized_graph = self.kernelize_graph(graph, period_df, stops_df, hub_list)

        # node_to_hub_df = self.create_egdes_to_hubs_df(graph, period_df, stops_df, hub_list)
        # first_hubs_df = self.create_first_hubs_df(first_stops_df, node_to_hub_df, stops_df)
        # extended_graph = self.extend_graph(graph, first_hubs_df)
        extended_graph = self.extend_graph(graph, first_stops_df)
        extended_transfers_df = self.create_extended_kernelized_transfers_df(extended_graph)

        def harmonic_sum(series):
            return int(reduce(lambda x, y: (x*y) / (x+y), series))
        extended_transfers_df = extended_transfers_df.groupby(['start_stop_id', 'end_stop_id', 'path'])\
            .agg({'duration': 'mean', 'period': harmonic_sum, 'route_id': lambda r: tuple(r)})
        extended_transfers_df = extended_transfers_df.reset_index()

        floyd_graph = nx.DiGraph()
        self.generate_floyd_nodes(floyd_graph, stops_df)
        self.generate_floyd_edges(floyd_graph, extended_transfers_df)
        distances = nx.floyd_warshall(floyd_graph)
        for key in distances.keys():
            distances[key] = dict(distances[key])

        return GraphData(floyd_graph, distances, stop_times_df, stops_df, routes_df, stops_df_by_name)

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
                        {'weight': int(row['duration'] + row['period'] * PERIOD_MULTIPLIER), 'route_ids': row['route_id'], 'path': row['path']}

        graph.add_edges_from(edge_generator())

    def create_extended_kernelized_transfers_df(self, extended_graph: nx.MultiDiGraph):
        graph = extended_graph

        def generator():
            for strat_stop, end_stop, route_id in graph.edges(keys=True):
                duration = graph.edges[strat_stop, end_stop, route_id]['duration']
                period = graph.edges[strat_stop, end_stop, route_id]['period']
                path = graph.edges[strat_stop, end_stop, route_id]['path']
                yield strat_stop, end_stop, route_id, int(duration), int(period), tuple(path)
        df = pd.DataFrame(generator(), columns=['start_stop_id', 'end_stop_id', 'route_id', 'duration', 'period', 'path'])
        return df

    def kernelize_graph(self, G, period_df, stops_df, hub_list):
        K_G = nx.MultiDiGraph()  # or DiGraph
        self.generate_kernelized_nodes(K_G, stops_df)
        self.generate_kernelized_edges(K_G, G, period_df, hub_list)
        return K_G

    def extract_graph(self, stops_df: pd.DataFrame, transfers_df: pd.DataFrame, first_stops_df: pd.DataFrame, period_df: pd.DataFrame):
        G = nx.MultiDiGraph()
        self.generate_nodes(G, stops_df)
        self.set_node_degrees(G, transfers_df)
        self.set_hubs(G, first_stops_df)
        self.generate_edges(G, transfers_df, period_df)
        return G

    def extend_graph(self, G: nx.MultiDiGraph, first_hubs_df: pd.DataFrame):
        first_hubs = list(first_hubs_df.drop_duplicates('stop_id')['stop_id'])
        for start_node in first_hubs:
            # TODO sth is wrong with first_hubs_df - no hub nodes in df
            first_routes_for_node = first_hubs_df['stop_id'] == start_node
            routes_ids_df = first_hubs_df[first_routes_for_node]
            routes_ids = list(routes_ids_df['route_id'])
            for route_id in routes_ids:
                edges = self.get_edges_data_from(G, start_node, route_id)
                for edge in edges:
                    _, _, first_neighbour, first_duration, period = edge
                    G.add_edges_from(self.extended_edges_generator(
                        G, start_node, first_neighbour, first_duration, route_id, period))
        return G

    def extended_edges_generator(self, G, start_node, first_neighbour, first_duration, route_id, period):
        edges = [(start_node, first_neighbour, first_duration)]
        already_visited = [start_node, first_neighbour]
        current_node = first_neighbour
        while True:
            next_edge = self.get_next_stop(G, current_node, route_id, already_visited)
            if next_edge is None:
                break
            _, _, next_node, duration, _ = next_edge
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
                    edges.add((int(edge['route_id']), node_from_id, node_to_id, int(edge['duration']), int(edge['period'])))
        return list(edges)

    def create_first_hubs_df(self, first_stops_df: pd.DataFrame, edges_to_hubs_df: pd.DataFrame, stops_df: pd.DataFrame):
        hubs_df = stops_df[stops_df['hub']]
        true_first_hubs_df = pd.merge(left=first_stops_df, right=hubs_df.reset_index(),
                                      left_on='stop_id', right_on='stop_id')
        true_first_hubs_df = true_first_hubs_df[['stop_id', 'route_id']]
        moved_first_hubs_df = pd.merge(left=first_stops_df, right=edges_to_hubs_df,
                                    left_on=['stop_id', 'route_id'], right_on=['hub_id', 'route_id'])
        moved_first_hubs_df = moved_first_hubs_df[['hub_id', 'route_id']]
        moved_first_hubs_df = moved_first_hubs_df.rename(columns={'hub_id': 'stop_id'})
        first_hubs_df = true_first_hubs_df.append(moved_first_hubs_df)
        first_hubs_df = first_hubs_df.drop_duplicates(['stop_id', 'route_id'])
        return first_hubs_df

    def create_egdes_to_hubs_df(self, graph, period_df, stops_df, hub_list):
        def edge_generator():
            for node_id, row in stops_df.iterrows():
                if row['hub'] == False:
                    for neighbour_id in graph.neighbors(node_id):
                        kernelized_duration = dict()
                        for edge in graph.get_edge_data(node_id, neighbour_id).values():
                            kernelized_duration[int(edge['route_id'])] = edge['duration']
                        result = self.get_neighbour_hub_distances(graph, [node_id], neighbour_id, kernelized_duration, hub_list)
                        if result is not None:
                            neighbour_hub, neighbour_distances = result
                            for route_id in neighbour_distances.keys():
                                if neighbour_distances[route_id] is not None:
                                    yield node_id, neighbour_hub, neighbour_distances[route_id], \
                                        int(period_df.loc[[int(route_id)]]['period']), int(route_id)

        df = pd.DataFrame(edge_generator(), columns=['stop_id', 'hub_id', 'duration', 'period', 'route_id'])
        return df

    def generate_kernelized_nodes(self, K_G: nx.MultiDiGraph, stops_df: pd.DataFrame):
        stops_df = stops_df[stops_df['hub']]
        stops_df.reset_index()

        def node_generator():
            for stop_id, row in stops_df.iterrows():
                yield stop_id, {'stop_name': row['stop_name'], 'stop_lat': row['stop_lat'], 'stop_lon': row['stop_lon']}

        K_G.add_nodes_from(node_generator())

    def generate_kernelized_edges(self, K_G, G, period_df, hub_list):
        def edge_generator():
            for hub_id in K_G.nodes():
                for neighbour_id in G.neighbors(hub_id):
                    kernelized_duration = dict()
                    for edge in G.get_edge_data(hub_id, neighbour_id).values():
                        kernelized_duration[int(edge['route_id'])] = edge['duration']
                    result = self.get_neighbour_hub_distances(G, [hub_id], neighbour_id, kernelized_duration, hub_list)
                    if result is not None:
                        neighbour_hub, neighbour_distances = result
                        for route_id in neighbour_distances.keys():
                            if neighbour_distances[route_id] is not None:
                                yield hub_id, neighbour_hub, int(route_id), {
                                    'duration': neighbour_distances[route_id],
                                    'period': int(period_df.loc[[int(route_id)]]['period']),
                                    'route_id': route_id,
                                    'path': []
                                }

        K_G.add_edges_from(edge_generator())

    def get_neighbour_hub_distances(self, graph, already_visited, node_id, kernelized_duration, hub_list):
        while node_id not in hub_list:
            neighbour_id = self.get_single_neighbour(graph, already_visited, node_id)
            if neighbour_id is None:
                return None
            for route_id in kernelized_duration.keys():
                if graph.has_edge(node_id, neighbour_id, route_id):
                    duration = graph.edges[node_id, neighbour_id, route_id]['duration']
                    if kernelized_duration[route_id] is not None:
                        kernelized_duration[route_id] += duration
                    else:
                        print("NONE")
                else:
                    kernelized_duration[route_id] = None
            already_visited.append(node_id)
            node_id = neighbour_id

        return node_id, kernelized_duration

    def get_single_neighbour(self, G, already_visited, node_id):
        for neighbor_id in G.neighbors(node_id):
            if neighbor_id not in already_visited:
                return neighbor_id
        return None

    def generate_nodes(self, G, stops_df):
        def node_generator():
            for stop_id, row in stops_df.iterrows():
                yield stop_id, {'stop_name': row['stop_name'], 'stop_lat': row['stop_lat'],
                                'stop_lon': row['stop_lon'], 'hub': row['hub']}
        G.add_nodes_from(node_generator())

    def generate_edges(self, G, transfers_df, period_df):
        map_df = transfers_df[[
            'route_id', 'start_stop_id', 'end_stop_id', 'duration']]
        avg_map_df = map_df.groupby(['route_id', 'start_stop_id', 'end_stop_id']).mean().reset_index()

        def edge_generator():
            for _, row in avg_map_df.iterrows():
                start_node = int(row['start_stop_id'])
                end_node = int(row['end_stop_id'])
                route_id =  row['route_id']
                duration = row['duration']
                period = int(period_df.loc[[int(route_id)]]['period'])
                yield start_node, end_node, route_id, \
                    {'route_id': route_id, 'duration': duration, 'period': period, 'path': []}

        G.add_edges_from(edge_generator())

    def set_hubs(self, G, first_stops_df):
        first_stops_df = first_stops_df[['stop_id']]
        first_stops_df = first_stops_df.drop_duplicates('stop_id')
        for node_id in G.nodes:
            stop = G.nodes[node_id]
            if node_id in first_stops_df.values and stop['degree'] > 1:
                stop['hub'] = True
            elif stop['degree'] > 2:
                stop['hub'] = True
            else:
                stop['hub'] = False

    def set_node_degrees(self, G, transfers_df):
        transfers_df = transfers_df.groupby(['start_stop_id']).count().reset_index()
        transfers_df = transfers_df[['start_stop_id', 'end_stop_id']]
        transfers_df = transfers_df.rename(columns={'start_stop_id': 'stop_id', 'end_stop_id': 'degree'},
                                           errors='raise')
        for node_id in G.nodes:
            stop = G.nodes[node_id]
            row = transfers_df.loc[transfers_df['stop_id'] == node_id]
            stop['degree'] = row.iloc[0]['degree']




