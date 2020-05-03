import copy
import pandas as pd
import networkx as nx

from static_map_module.ExtractedMap import ExtractedMap
from static_timetable_module.gtfs_static.ExtractedData import ExtractedData


class MapExtractor:
    def extract_map(self, extracted_data: ExtractedData):
        stops_df = extracted_data.stops_df
        transfers_trips_df = extracted_data.transfers_trips_df
        stop_times_trips_df = extracted_data.stop_times_trips_df
        avg_durations_df = extracted_data.avg_durations_df
        first_stops_df = extracted_data.first_stops_df
        frequency_df = extracted_data.frequency_df

        G = self.extract_graph(stops_df, transfers_trips_df, first_stops_df)
        K_G = self.kernelize_graph(G)

        distances, paths = self.floyd_warshall(K_G)

        return ExtractedMap(G, K_G, distances, paths)


    def floyd_warshall(self, G):
        distances = {}
        paths = {}

        def distance(node_1, node_2):
            if (node_1, node_2) not in distances.keys():
                return float("inf")
            return distances[(node_1, node_2)]

        def get_edge_list(node_1, G):
            def edges_inner():
                for node_2 in G.neighbors(node_1):
                    for edge in G.get_edge_data(node_1, node_2).values():
                        yield node_2, edge['duration']

            return list(edges_inner())

        for node in G.nodes():
            for neighbour, duration in get_edge_list(node, G):
                distances[(node, neighbour)] = duration
                paths[(node, neighbour)] = []
        for k in G.nodes():
            print(".", end="")
            for i in G.nodes():
                for j in G.nodes():
                    if distance(i, j) > distance(i, k) + distance(k, j):
                        distances[(i, j)] = distance(i, k) + distance(k, j)
                        path = copy.copy(paths[(i, k)])
                        path.append(k)
                        path.extend(paths[(k, j)])
                        paths[(i, j)] = path
        return distances, paths

    def kernelize_graph(self, G):
        K_G = nx.MultiDiGraph()  # or DiGraph
        self.generate_kernelized_nodes(K_G, G)
        self.generate_kernelized_edges(K_G, G)
        return K_G

    def extract_graph(self, stops_df: pd.DataFrame, transfers_df: pd.DataFrame, first_stops_df: pd.DataFrame):
        G = nx.MultiDiGraph()
        self.generate_nodes(G, stops_df)
        self.set_node_degrees(G, transfers_df)
        self.set_hubs(G, first_stops_df)
        self.generate_edges(G, transfers_df)
        return G

    def generate_kernelized_nodes(self, K_G, G):
        def node_generator():
            for node_id in G.nodes:
                stop = G.nodes[node_id]
                if stop['hub']:
                    yield node_id, \
                          {'stop_name': stop['stop_name'], 'stop_lat': stop['stop_lat'], 'stop_lon': stop['stop_lon']}
        K_G.add_nodes_from(node_generator())

    def generate_kernelized_edges(self, K_G, G):
        def edge_generator():
            for hub_id in K_G.nodes():
                kernelized_duration = {}
                for node_1, node_2 in G.edges([hub_id]):
                    for edge in G.get_edge_data(node_1, node_2).values():
                        kernelized_duration[edge['route_id']] = edge['duration']
                    result = self.get_neighbour_hub_distances(G, [node_1], node_2, kernelized_duration)
                    if result is not None:
                        neighbour_hub, neighbour_distances = result
                        for route_id in neighbour_distances.keys():
                            yield hub_id, neighbour_hub, \
                                  {'duration': neighbour_distances[route_id], 'route_id': route_id}

        K_G.add_edges_from(edge_generator())

    def get_neighbour_hub_distances(self, G, already_visited, current_node, kernelized_duration):
        while not G.nodes[current_node]['hub']:
            neighbour_node = self.get_single_neighbour(G, already_visited, current_node)
            if neighbour_node is None:
                return None
            for edge in G.get_edge_data(current_node, neighbour_node).values():
                if edge['route_id'] not in kernelized_duration.keys():
                    kernelized_duration[edge['route_id']] = 0
                    print(edge['route_id'])
                kernelized_duration[edge['route_id']] += edge['duration']
            already_visited.append(current_node)
            current_node = neighbour_node

        return current_node, kernelized_duration

    def get_single_neighbour(self, G, already_visited, current_node):
        for node_1, node_2 in G.edges([current_node]):
            if node_2 not in already_visited:
                return node_2
        return None

    def generate_nodes(self, G, stops_df):
        def node_generator():
            for stop_id, row in stops_df.iterrows():
                yield stop_id, {'stop_name': row['stop_name'], 'stop_lat': row['stop_lat'], 'stop_lon': row['stop_lon']}

        G.add_nodes_from(node_generator())

    def generate_edges(self, G, transfers_df):
        map_df = transfers_df[[
            'route_id', 'start_stop_id', 'end_stop_id', 'duration']]
        avg_map_df = map_df.groupby(['route_id', 'start_stop_id', 'end_stop_id']).mean().reset_index()

        def edge_generator():
            for _, row in avg_map_df.iterrows():
                yield int(row['start_stop_id']), int(row['end_stop_id']), \
                      {'duration': row['duration'], 'route_id': row['route_id']}

        G.add_edges_from(edge_generator())

    def set_hubs(self, G, first_stops_df):
        first_stop_df = first_stops_df[['stop_id']]
        for node_id in G.nodes:
            stop = G.nodes[node_id]
            if node_id in first_stop_df.values and stop['degree'] > 1:
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




