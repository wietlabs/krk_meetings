from src.data_provider.Downloader import Downloader
from src.data_provider.gtfs_realtime.VehiclePositionsParser import VehiclePositionsParser

if __name__ == '__main__':
    downloader = Downloader()
    vehicle_positions_pb_T, vehicle_positions_pb_A = downloader.download_vehicle_positions()

    parser = VehiclePositionsParser()
    vehicle_positions_df_T = parser.parse(vehicle_positions_pb_T)
    vehicle_positions_df_A = parser.parse(vehicle_positions_pb_A)
