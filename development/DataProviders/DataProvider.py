from static_map_module.FloydDataExtractor import FloydDataExtractor
from gtfs_static.Extractor import Extractor
from gtfs_static.Parser import Parser
from DataClasses.FloydSolverData import FloydSolverData
from pathlib import Path


class DataProvider:
    @staticmethod
    def parse_data():
        parser = Parser()
        parsed_data = parser.parse(Path(__file__).parent / 'GTFS_KRK_A')
        parsed_data.save(Path(__file__).parent / 'tmp' / 'parsed_data.pickle')
        return parsed_data

    @staticmethod
    def parse_and_extract_floyd_data():
        parser = Parser()
        extractor = FloydDataExtractor()
        # Loading parsed data
        parsed_data = parser.parse(Path(__file__).parent / 'GTFS_KRK_A')
        stops_df = parsed_data.stops_df
        transfers_df = parsed_data.transfers_df
        stop_times_df = parsed_data.stop_times_df
        trips_df = parsed_data.trips_df
        routes_df = parsed_data.routes_df
        calendar_df = parsed_data.calendar_df

        # Basic extraction
        route_ids_df = extractor.create_route_ids_df(stop_times_df)
        period_df = extractor.create_period_df(stop_times_df, route_ids_df)
        stops_df = extractor.set_first_and_last_stop(stop_times_df, route_ids_df, stops_df)
        stops_df = extractor.extend_stops_df(transfers_df, stops_df)
        stops_df_by_name = stops_df.reset_index().set_index('stop_name')
        transfers_df = extractor.create_transfers_trips_df(transfers_df, route_ids_df)
        stop_times_df = extractor.create_stop_times_trips_df_for_service_id(stop_times_df, route_ids_df)
        day_to_services_dict = extractor.get_day_to_services_dict(calendar_df)
        routes_df = extractor.create_routes_trips_df(trips_df, routes_df)\
            .set_index(['service_id', 'block_id', 'trip_num'])

        # Floyd extraction
        graph = extractor.extract_graph(stops_df, transfers_df, period_df)
        extended_graph = extractor.extend_graph(graph, stops_df)
        extended_transfers_df = extractor.create_extended_transfers_df(extended_graph)
        floyd_graph = extractor.create_floyd_graph(extended_transfers_df, stops_df)
        kernelized_floyd_graph = extractor.create_kernelized_floyd_graph(floyd_graph, stops_df)
        distances = extractor.get_distances(floyd_graph)

        floyd_data = FloydSolverData(floyd_graph, kernelized_floyd_graph, distances, day_to_services_dict,
                                     stop_times_df, stops_df, routes_df, stops_df_by_name)
        floyd_data.save(Path(__file__).parent / 'tmp' / 'graph_data.pickle')
        return floyd_data

    @staticmethod
    def load_floyd_data():
        extracted_data = FloydSolverData.load(Path(__file__).parent / 'tmp' / 'graph_data.pickle')
        return extracted_data
