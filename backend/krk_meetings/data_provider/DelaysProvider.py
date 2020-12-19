import time

from krk_meetings.data_provider.DelaysExtractor import DelaysExtractor
from krk_meetings.data_provider.Downloader import Downloader
from krk_meetings.data_provider.data_provider_utils import load_property_from_config_json
from krk_meetings.data_provider.gtfs_realtime.VehiclePositionsMerger import VehiclePositionsMerger
from krk_meetings.data_provider.gtfs_realtime.VehiclePositionsParser import VehiclePositionsParser
from krk_meetings.rabbitmq.RmqProducer import RmqProducer
from krk_meetings.exchanges import EXCHANGES, MESSAGES
from krk_meetings.config import FloydDataPaths
import socket
import pandas as pd
from krk_meetings.logger import get_logger

logger = get_logger(__name__)


def start_delays_provider():
    delays_provider = DelaysProvider()
    delays_provider.start()


class DelaysProvider:
    def __init__(self, data_path=FloydDataPaths):
        self.delays_producer = RmqProducer(EXCHANGES.DELAYS_PROVIDER.value)
        self.downloader = Downloader()
        self.parser = VehiclePositionsParser()
        self.merger = VehiclePositionsMerger()
        self.extractor = DelaysExtractor()
        self.data_path = data_path

    def start(self):
        self.delays_producer.start()
        logger.info("DelaysProvider: has started.")
        while True:
            try:
                vehicle_positions_pb_T, vehicle_positions_pb_A = self.downloader.download_vehicle_positions()
                vehicle_positions_df_T = self.parser.parse(vehicle_positions_pb_T)
                vehicle_positions_df_A = self.parser.parse(vehicle_positions_pb_A)

                services_id_offset = len(load_property_from_config_json("services")[0])
                vehicle_positions_df = self.merger.merge(vehicle_positions_df_T, vehicle_positions_df_A, services_id_offset)

                stop_times_df = pd.read_pickle(self.data_path.stops_times_df.value)
                delays_df = self.extractor.extract(vehicle_positions_df, stop_times_df)

                delays_df.to_pickle(self.data_path.delays_df.value)
                self.delays_producer.send_msg(MESSAGES.DELAYS_UPDATED.value, lost_stream_msg="Solvers are down.")
                logger.info("DelaysProvider: delays updated")
                time.sleep(120)
            except socket.gaierror:
                time.sleep(30)
            except (TypeError, FileNotFoundError):
                logger.warn(
                    f"Delays provider: Some pickles in data directory are missing this service won't "
                    f"work without them. Wait for DataProvider to finish processing GTFS files.")
                time.sleep(30)
                continue



if __name__ == "__main__":
    start_delays_provider()
