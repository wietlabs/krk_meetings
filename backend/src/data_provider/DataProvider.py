import socket
import time

from src.config import FloydDataPaths, DEFAULT_EXTRACTOR_CONFIGURATION
from src.data_provider.Downloader import Downloader
from src.data_provider.Extractor import Extractor
from src.data_provider.gtfs_static.Corrector import Corrector
from src.data_provider.gtfs_static.Merger import Merger
from src.data_provider.gtfs_static.Parser import Parser
from src.data_provider.data_provider_utils import save_property_to_config_json, load_property_from_config_json
from src.rabbitmq.RmqProducer import RmqProducer
from src.exchanges import EXCHANGES, MESSAGES


def start_data_provider():
    data_provider = DataProvider()
    data_provider.start()


class DataProvider:
    def __init__(self, data_path=FloydDataPaths, configuration=DEFAULT_EXTRACTOR_CONFIGURATION):
        self.floyd_data_producer = RmqProducer(EXCHANGES.DATA_PROVIDER.value)
        self.downloader = Downloader()
        self.parser = Parser()
        self.merger = Merger()
        self.corrector = Corrector()
        self.extractor = Extractor(configuration)
        self.data_path = data_path
        self.alive = False

    def start(self):
        self.floyd_data_producer.start()
        self.alive = True
        print("DataProvider: has started.")
        while self.alive:
            try:
                new_update_date = self.downloader.get_last_update_time()
                last_update_date = self.load_update_date()
                if last_update_date is None or new_update_date > last_update_date:
                    self.process_data()
                    save_property_to_config_json("update_date", new_update_date.strftime("%Y-%m-%d %H:%M:%S"))
                    self.floyd_data_producer.send_msg(MESSAGES.DATA_UPDATED.value, lost_stream_msg="Solvers are down.")
            except socket.gaierror:
                print("DataProvider: internet connection lost")
            time.sleep(3600)

    def stop(self):
        self.floyd_data_producer.stop()
        self.alive = False

    @staticmethod
    def load_update_date():
        load_property_from_config_json("update_date")

    def process_data(self):
        print("DataProvider: updating data")
        gtfs_zip_T, gtfs_zip_A = self.downloader.download_gtfs_static_data()
        parsed_data_T = self.parser.parse(gtfs_zip_T)
        parsed_data_A = self.parser.parse(gtfs_zip_A)
        print("DataProvider: data parsed")

        merged_data, service_id_offset = self.merger.merge(parsed_data_T, parsed_data_A)
        print("DataProvider: data merged")

        corrected_data = self.corrector.correct(merged_data)
        print("DataProvider: data corrected")

        extracted_data = self.extractor.extract(corrected_data)
        print("DataProvider: data extracted")

        save_property_to_config_json("services", [list(parsed_data_T.calendar_df.index),
                                                  list(parsed_data_A.calendar_df.index + service_id_offset)])
        extracted_data.save(self.data_path)
        print("DataProvider: data saved")


if __name__ == "__main__":
    data_provider = DataProvider()
    data_provider.process_data()
    data_provider.stop()
