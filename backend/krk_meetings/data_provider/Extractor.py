import copy
from functools import reduce
import pandas as pd
import networkx as nx

from krk_meetings.data_classes.ExtractedData import ExtractedData
from krk_meetings.data_classes.ParsedData import ParsedData
from krk_meetings.data_provider.data_provider_utils import is_nightly, get_walking_time, load_property_from_config_json
from krk_meetings.config import DEFAULT_EXTRACTOR_CONFIGURATION, FloydDataPaths
from krk_meetings.utils import load_pickle
from krk_meetings.logger import get_logger

logger = get_logger(__name__)


class Extractor:
    def __init__(self, configuration=DEFAULT_EXTRACTOR_CONFIGURATION):
        super().__init__()
        self.configuration = configuration

    def extract(self, merged_data: ParsedData) -> ExtractedData:
        stops_df = merged_data.stops_df
        transfers_df = merged_data.transfers_df
        stop_times_df = merged_data.stop_times_df
        trips_df = merged_data.trips_df
        routes_df = merged_data.routes_df
        calendar_df = merged_data.calendar_df
        calendar_dates_df = merged_data.calendar_dates_df

        # Basic extraction
        route_ids_df = self.create_route_ids_df(stop_times_df)
        stops_df = self.set_first_and_last_stop(stop_times_df, route_ids_df, stops_df)
        stops_df_by_name = stops_df.reset_index().set_index('stop_name')
        transfers_df = self.create_transfers_trips_df(transfers_df, route_ids_df)
        current_stop_times_df = self.create_stop_times_trips_df_for_service_id(stop_times_df, route_ids_df)
        day_to_services_dict = self.get_day_to_services_dict(calendar_df)
        routes_df = self.create_routes_trips_df(trips_df, routes_df, route_ids_df)
        services_list = self.get_services_list(calendar_df)
        routes_to_stops_dict = self.create_route_to_stops_dict(stop_times_df, route_ids_df)
        exception_days = self.create_exception_days_dict(calendar_dates_df)
        period_df = self.create_period_df(stop_times_df, route_ids_df, routes_df)

        # Floyd extraction
        current_stop_times_df['service'] = current_stop_times_df.index.get_level_values('service_id')
        current_stop_times_df = current_stop_times_df.reset_index('stop_sequence')
        graph = self.extract_graph(stops_df, transfers_df, period_df)
        extended_graph = self.extend_graph(graph, stops_df)
        adjacent_stops = self.get_adjacent_stops_dict(stops_df)
        floyd_transfers_df = self.create_floyd_transfers_df(extended_graph, adjacent_stops)
        stops_df = self.extend_stops_df(transfers_df, adjacent_stops, stops_df)
        floyd_graph = self.create_floyd_graph(floyd_transfers_df, stops_df)
        kernelized_floyd_graph = self.create_kernelized_floyd_graph(floyd_graph, stops_df)
        distances = self.get_distances(floyd_graph)

        previous_stop_times_df = copy.deepcopy(current_stop_times_df)
        previous_stop_times_df['departure_time'] = previous_stop_times_df['departure_time'].apply(
            lambda t: t - 24 * 3600)
        previous_stop_times_df = previous_stop_times_df[previous_stop_times_df['departure_time'] >= 0]

        next_stop_times_df = copy.deepcopy(current_stop_times_df)
        next_stop_times_df['departure_time'] = next_stop_times_df['departure_time'].apply(lambda t: t + 24 * 3600)
        next_stop_times_df = next_stop_times_df[next_stop_times_df['departure_time'] <= 36 * 3600]

        current_stop_times_dict = self.transform_stop_times_df_to_dict(stops_df, current_stop_times_df,
                                                                            services_list)
        previous_stop_times_dict = self.transform_stop_times_df_to_dict(stops_df, previous_stop_times_df,
                                                                             services_list)
        next_stop_times_dict = self.transform_stop_times_df_to_dict(stops_df, next_stop_times_df, services_list)

        return ExtractedData(floyd_graph=floyd_graph,
                             kernelized_floyd_graph=kernelized_floyd_graph,
                             distances=distances,
                             day_to_services_dict=day_to_services_dict,
                             current_stop_times_dict=current_stop_times_dict,
                             previous_stop_times_dict=previous_stop_times_dict,
                             next_stop_times_dict=next_stop_times_dict,
                             routes_to_stops_dict=routes_to_stops_dict,
                             adjacent_stops=adjacent_stops,
                             exception_days=exception_days,
                             stops_df=stops_df,
                             routes_df=routes_df,
                             stops_df_by_name=stops_df_by_name,
                             stop_times_df=stop_times_df)


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
            times_by_stop = stop_times_df[stop_times_df['stop_id'] == stop_id]
            stop_times_dict[stop_id] = {}
            for service in services_list:
                stop_times_dict[stop_id][service] = times_by_stop[times_by_stop['service'] == service] \
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
        df = df[['route_id', 'service_id', 'departure_time']]
        df = df.groupby(['route_id', 'service_id']).agg({'departure_time': ['count', 'min', 'max']})
        df.columns = ['count', 'min', 'max']
        df = df.reset_index()
        services = load_property_from_config_json('services')
        df['period'] = df.apply(lambda row: self.get_period(row['route_id'], row['service_id'], row['count'],
                                                            routes_df, services), axis=1)
        df = df.reset_index()
        df = df[['route_id', 'period']]
        df = df.drop_duplicates('route_id')
        df = df.set_index('route_id')
        return df

    def get_period(self, route_id: int, service_id: int, count: int, routes_df: pd.DataFrame, services: list):
        service_count = 1
        for service in services:
            if service_id in service:
                service_count = len(service)
                break

        nightly = is_nightly(routes_df.at[route_id, 'route_name'], self.configuration.nightly_route_ranges)
        if nightly:
            running_hours = self.configuration.nightly_hours
            multiplier = self.configuration.nightly_period_multiplier
        else:
            running_hours = self.configuration.daily_hours
            multiplier = self.configuration.daily_period_multiplier
        return int(running_hours * 3600 / count * service_count * multiplier)

    def get_adjacent_stops_dict(self, stops_df: pd.DataFrame) -> dict:
        try:
            walking_distances_pickle = load_pickle(FloydDataPaths.api_walking_distances.value)
            logger.info("api_walking_distances.pickle found")
        except FileNotFoundError:
            walking_distances_pickle = {'distances': {}, 'stop_list': []}
            logger.warn("api_walking_distances.pickle not found, walking time will be calculated "
                        "from distance in a straight line. To create api_walking_distances.pickle, "
                        "run krk_meetings/scripts/reparse_walking_distances.py")
        api_walking_distances = walking_distances_pickle['distances']
        api_stop_list = walking_distances_pickle['stop_list']
        stops_df = stops_df[['stop_name', 'stop_lon', 'stop_lat']]
        adjacent_stops = {}
        for id_1, name_1, lat_1, lon_1 in stops_df.itertuples():
            for id_2, name_2, lat_2, lon_2 in stops_df.itertuples():
                if id_1 == id_2:
                    continue
                if name_1 in api_stop_list and name_2 in api_stop_list:
                    if (name_1, name_2) not in api_walking_distances:
                        continue
                    duration = api_walking_distances[(name_1, name_2)]
                else:
                    duration = get_walking_time(lon_1, lat_1, lon_2, lat_2)
                if duration <= self.configuration.max_walking_time_in_minutes * 60:
                    adjacent_stops[id_1, id_2] = duration
        return adjacent_stops

    @staticmethod
    def get_day_to_services_dict(calendar_df: pd.DataFrame) -> dict:
        day_to_services = {i: [] for i in range(7)}
        for service_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday in calendar_df.itertuples():
            if monday: day_to_services[0].append(service_id)
            if tuesday: day_to_services[1].append(service_id)
            if wednesday: day_to_services[2].append(service_id)
            if thursday: day_to_services[3].append(service_id)
            if friday: day_to_services[4].append(service_id)
            if saturday: day_to_services[5].append(service_id)
            if sunday: day_to_services[6].append(service_id)
        return day_to_services

    @staticmethod
    def get_services_list(calendar_df) -> list:
        return list(calendar_df.index)

    @staticmethod
    def create_route_ids_df(stop_times_df: pd.DataFrame) -> pd.DataFrame:
        routes_path_df = stop_times_df.groupby(['block_id', 'trip_num', 'service_id']).agg(
            {'peron_id': lambda x: tuple(x)})
        routes_ids_df = routes_path_df.drop_duplicates('peron_id')
        routes_ids_df = routes_ids_df.reset_index()[['peron_id']]
        routes_ids_df = routes_ids_df.reset_index().rename(columns={'index': 'route_id'})
        routes_ids_df = routes_ids_df.set_index('peron_id')
        routes_ids_df = routes_path_df.reset_index().merge(routes_ids_df, on='peron_id')
        routes_ids_df = routes_ids_df[['block_id', 'trip_num', 'service_id', 'route_id']]
        routes_ids_df = routes_ids_df.set_index(['block_id', 'trip_num', 'service_id'])
        return routes_ids_df

    @staticmethod
    def create_routes_trips_df(trips_df: pd.DataFrame, routes_df: pd.DataFrame, routes_ids_df: pd.DataFrame
                               ) -> pd.DataFrame:
        routes_df = trips_df.reset_index().merge(routes_df, on='route_id')[
            ['service_id', 'block_id', 'trip_num', 'trip_headsign', 'route_short_name']]
        routes_df = routes_df.rename(columns={'route_short_name': 'route_name', 'trip_headsign': 'headsign'})
        routes_df = routes_df.set_index(['service_id', 'block_id', 'trip_num'])
        routes_df = routes_df.join(routes_ids_df).drop_duplicates('route_id')
        routes_df = routes_df.set_index('route_id')[['route_name', 'headsign']]
        return routes_df

    @staticmethod
    def create_transfers_trips_df(transfers_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> pd.DataFrame:
        df = transfers_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df = df[['route_id', 'block_id', 'trip_num', 'service_id', 'start_time', 'end_time', 'start_stop_id',
                 'end_stop_id', 'duration']]
        return df

    @staticmethod
    def create_stop_times_trips_df_for_service_id(stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame
                                                  ) -> pd.DataFrame:
        df = stop_times_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df = df[['stop_id', 'peron_id', 'departure_time', 'route_id']]
        return df

    @staticmethod
    def create_avg_durations_df(transfers_df: pd.DataFrame) -> pd.DataFrame:
        return transfers_df[['start_stop_id', 'end_stop_id', 'duration']] \
            .groupby(['start_stop_id', 'end_stop_id']).mean()

    @staticmethod
    def set_first_and_last_stop(stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame, stops_df: pd.DataFrame
                                ) -> pd.DataFrame:
        stop_times_df = stop_times_df

        stop_times_df = stop_times_df.join(route_ids_df)
        stop_times_df.sort_values(by='stop_sequence', inplace=True)

        is_first = stop_times_df.drop_duplicates(subset=['route_id'], keep='first')
        is_last = stop_times_df.drop_duplicates(subset=['route_id'], keep='last')
        is_first = is_first['stop_id'].tolist()
        is_last = is_last['stop_id'].tolist()

        stops_df.reset_index(inplace=True)
        stops_df['is_first'] = stops_df['stop_id'].apply(lambda x: x in is_first)
        stops_df['is_last'] = stops_df['stop_id'].apply(lambda x: x in is_last)
        stops_df.set_index('stop_id', inplace=True)
        return stops_df

    @staticmethod
    def extend_stops_df(transfer_df: pd.DataFrame, adjacent_stops: dict, stops_df: pd.DataFrame) -> pd.DataFrame:
        hubs_df = transfer_df[['start_stop_id', 'end_stop_id']]
        adjacent_stops_df = pd.DataFrame.from_dict(data={'start_stop_id': [key[0] for key in adjacent_stops],
                                                         'end_stop_id': [key[1] for key in adjacent_stops]})
        hubs_df = pd.concat([hubs_df, adjacent_stops_df])
        hubs_df = hubs_df.drop_duplicates(subset=['start_stop_id', 'end_stop_id'])
        hubs_df = hubs_df.groupby('start_stop_id').count()
        hubs_df = stops_df.reset_index().merge(hubs_df, left_on='stop_id', right_on='start_stop_id', how="outer")
        hubs_df.fillna(0, inplace=True)
        hubs_df = hubs_df[['stop_id', 'end_stop_id']].set_index('stop_id')
        def is_hub(row):
            if row['is_first'] and row['is_last']:
                return hubs_df.at[(row['stop_id'], 'end_stop_id')] > 1
            return hubs_df.at[(row['stop_id'], 'end_stop_id')] > 2

        stops_df = stops_df.reset_index()
        stops_df['hub'] = stops_df.apply(is_hub, axis=1)

        stops_df = stops_df.set_index('stop_id')
        return stops_df

    @staticmethod
    def create_route_to_stops_dict(stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> dict:
        stop_times_df = stop_times_df.reset_index()
        df = stop_times_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df.drop_duplicates(subset=['route_id', 'stop_sequence'], inplace=True)
        df = df[['route_id', 'stop_sequence', 'stop_id', 'peron_id']]
        df.sort_values('stop_sequence', inplace=True, ascending=True)
        route_to_stops_dict = {}
        for _, route_id, stop_sequence, stop_id, peron_id in df.itertuples():
            if route_id not in route_to_stops_dict:
                route_to_stops_dict[route_id] = []
            route_to_stops_dict[route_id].append(stop_id)
        return route_to_stops_dict

    @staticmethod
    def create_exception_days_dict(calendar_dates_df: pd.DataFrame):
        exception_days = {}
        for index, service_id, date, exception_type in calendar_dates_df.itertuples():
            if date not in exception_days:
                exception_days[date] = {"services_to_add": [], "services_to_remove": []}
            if exception_type == 1:
                exception_days[date]["services_to_add"].append(service_id)
            elif exception_type == 2:
                exception_days[date]["services_to_remove"].append(service_id)
        return exception_days

