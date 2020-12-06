import time

from src.data_provider.DelaysExtractor import DelaysExtractor
from src.data_provider.Downloader import Downloader
from src.data_provider.data_provider_utils import load_property_from_config_json
from src.data_provider.gtfs_realtime.VehiclePositionsMerger import VehiclePositionsMerger
from src.data_provider.gtfs_realtime.VehiclePositionsParser import VehiclePositionsParser
from src.rabbitmq.RmqProducer import RmqProducer
from src.exchanges import EXCHANGES, MESSAGES
from src.config import FloydDataPaths
import socket
import pandas as pd


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
        print("DelaysProvider: has started.")
        while True:
            try:
                vehicle_positions_pb_T, vehicle_positions_pb_A = self.downloader.download_vehicle_positions()
                vehicle_positions_df_T = self.parser.parse(vehicle_positions_pb_T)
                vehicle_positions_df_A = self.parser.parse(vehicle_positions_pb_A)

                services_id_offset = len(load_property_from_config_json("services")[0])
                vehicle_positions_df = self.merger.merge(vehicle_positions_df_T, vehicle_positions_df_A, services_id_offset)

                delays_df = self.extractor.extract(vehicle_positions_df)

                delays_df.to_pickle(self.data_path.delays_df.value)
                self.delays_producer.send_msg(MESSAGES.DELAYS_UPDATED.value, lost_stream_msg="Solvers are down.")
                print("DelaysProvider: delays updated")
                time.sleep(120)
            except socket.gaierror:
                time.sleep(30)


if __name__ == "__main__":
    start_delays_provider()
