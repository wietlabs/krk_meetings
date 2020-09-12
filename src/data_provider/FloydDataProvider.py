import copy
import json
import time
from datetime import datetime

from src.data_classes.ParsedData import ParsedData
from src.data_provider.Downloader import Downloader
from src.data_provider.Merger import Merger
from src.data_provider.FloydDataExtractor import FloydDataExtractor
from src.data_provider.Parser import Parser
from src.data_classes.FloydSolverData import FloydSolverData
from pathlib import Path
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.config import EXCHANGES

FLOYD_DATA_PATH = Path(__file__).parent / 'data' / 'tmp' / 'floyd_data.pickle'
CONFIG_JSON_PATH = Path(__file__).parent / 'data' / 'tmp' / 'config.json'


def start_data_provider():
    data_provider = FloydDataProvider()
    data_provider.start()


class FloydDataProvider:
    def __init__(self):
        self.floyd_data_producer = RmqProducer(EXCHANGES.FLOYD_DATA.value)
        self.downloader = Downloader()

    def start(self):
        print("FloydDataProvider: has started.")
        while True:
            new_update_date = self.downloader.get_last_update_time()
            last_update_date = self.load_update_date()
            if new_update_date > last_update_date:
                merged_data = self.downloader.download_merged_data()
                self.extract_floyd_data(merged_data)
                self.save_update_date(new_update_date)
                self.floyd_data_producer.send_msg("update data")
                print("FloydDataProvider: data updated")
            time.sleep(3600)

    def stop(self):
        pass

    @staticmethod
    def extract_floyd_data(merged_data: ParsedData):
        extractor = FloydDataExtractor()
        stops_df = merged_data.stops_df
        transfers_df = merged_data.transfers_df
        stop_times_df = merged_data.stop_times_df
        trips_df = merged_data.trips_df
        routes_df = merged_data.routes_df
        calendar_df = merged_data.calendar_df

        # Basic extraction
        route_ids_df = extractor.create_route_ids_df(stop_times_df)
        period_df = extractor.create_period_df(stop_times_df, route_ids_df)
        stops_df = extractor.set_first_and_last_stop(stop_times_df, route_ids_df, stops_df)
        stops_df = extractor.extend_stops_df(transfers_df, stops_df)
        stops_df_by_name = stops_df.reset_index().set_index('stop_name')
        transfers_df = extractor.create_transfers_trips_df(transfers_df, route_ids_df)
        stop_times_0_df = extractor.create_stop_times_trips_df_for_service_id(stop_times_df, route_ids_df)
        day_to_services_dict = extractor.get_day_to_services_dict(calendar_df)
        routes_df = extractor.create_routes_trips_df(trips_df, routes_df, route_ids_df)
        services_list = extractor.get_services_list(calendar_df)
        routes_to_stops_dict = extractor.create_route_to_stops_dict(stop_times_df, route_ids_df)

        # Floyd extraction
        stop_times_0_df['service'] = stop_times_0_df.index.get_level_values('service_id')
        stop_times_0_df = stop_times_0_df.reset_index('stop_sequence')
        graph = extractor.extract_graph(stops_df, transfers_df, period_df)
        extended_graph = extractor.extend_graph(graph, stops_df)
        extended_transfers_df = extractor.create_extended_transfers_df(extended_graph)
        floyd_graph = extractor.create_floyd_graph(extended_transfers_df, stops_df)
        kernelized_floyd_graph = extractor.create_kernelized_floyd_graph(floyd_graph, stops_df)
        distances = extractor.get_distances(floyd_graph)
        stop_times_24_df = copy.deepcopy(stop_times_0_df)
        stop_times_24_df['departure_time'] = stop_times_24_df['departure_time'].apply(lambda t: t + 24 * 3600)
        stop_times_0_dict = extractor.transform_stop_times_df_to_dict(stops_df, stop_times_0_df, services_list)
        stop_times_24_dict = extractor.transform_stop_times_df_to_dict(stops_df, stop_times_24_df, services_list)

        floyd_data = FloydSolverData(floyd_graph, kernelized_floyd_graph, distances, day_to_services_dict,
                                    stop_times_0_dict, stop_times_24_dict, routes_to_stops_dict, stops_df, routes_df, stops_df_by_name)
        floyd_data.save(FLOYD_DATA_PATH)
        return floyd_data

    @staticmethod
    def load_floyd_data() -> FloydSolverData:
        floyd_data = FloydSolverData.load(FLOYD_DATA_PATH)
        return floyd_data

    @staticmethod
    def load_update_date():
        with open(CONFIG_JSON_PATH) as json_file:
            update_date = json.load(json_file)["update_date"]
            update_date = datetime.strptime(update_date, "%Y-%m-%d %H:%M:%S")
        return update_date

    @staticmethod
    def save_update_date(update_date):
        with open(CONFIG_JSON_PATH, 'w') as json_file:
            update_date = {
                "update_date": update_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            json.dump(update_date, json_file)


if __name__ == "__main__":
    start_data_provider()
