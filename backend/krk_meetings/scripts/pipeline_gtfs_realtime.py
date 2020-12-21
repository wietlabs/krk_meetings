from krk_meetings.data_provider.Downloader import Downloader
from krk_meetings.data_provider.gtfs_realtime.VehiclePositionsMerger import VehiclePositionsMerger
from krk_meetings.data_provider.gtfs_realtime.VehiclePositionsParser import VehiclePositionsParser

if __name__ == '__main__':
    downloader = Downloader()
    vehicle_positions_pb_T, vehicle_positions_pb_A = downloader.download_vehicle_positions()

    parser = VehiclePositionsParser()
    vehicle_positions_df_A = parser.parse(vehicle_positions_pb_A)
    vehicle_positions_df_T = parser.parse(vehicle_positions_pb_T)

    merger = VehiclePositionsMerger()
    vehicle_positions_df = merger.merge(vehicle_positions_df_A, vehicle_positions_df_T, services_id_offset=3)
