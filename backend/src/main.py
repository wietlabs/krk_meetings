import pandas as pd
from datetime import datetime
from src.config import FloydDataPaths
from src.data_provider.Downloader import Downloader
from src.data_provider.gtfs_realtime.VehiclePositionsParser import VehiclePositionsParser
from src.utils import load_pickle
import numpy as np

if __name__ == "__main__":

    downloader = Downloader()
    vehicle_positions_pb_T, vehicle_positions_pb_A = downloader.download_vehicle_positions()

    parser = VehiclePositionsParser()
    vehicle_positions_df_T = parser.parse(vehicle_positions_pb_T)
    vehicle_positions_df_A = parser.parse(vehicle_positions_pb_A)
    vehicle_positions_df_A['service_id'] += 3  # service_id_offset needs stored when updating GTFS Static data
    vehicle_positions_df = pd.concat((vehicle_positions_df_T, vehicle_positions_df_A))  # TODO: move
    vehicle_positions_df.set_index(['service_id', 'block_id', 'trip_num', 'stop_sequence'], inplace=True)
    stop_times_df = pd.read_pickle(FloydDataPaths.stops_times_df.value)
    delays_df = vehicle_positions_df.join(stop_times_df)
    delays_df = delays_df.dropna()
    delays_df['delay'] = delays_df.apply(lambda row: (int(row['timestamp'] - row['departure_time'] + 3600) % (3600 * 24)), axis=1)
    delays_df['delay'] = delays_df['delay'].apply(lambda delay: delay if delay < 12 * 3600 else delay - 24*3600)
    delays_df = delays_df[delays_df['delay'] > -600]
    delays_df.reset_index(['stop_sequence'], inplace=True)
    delays_df = delays_df[['delay']]
    delays_df.to_pickle(FloydDataPaths.delays_df.value)

    result_df = pd.merge(stop_times_df, delays_df, on=['service_id', 'block_id', 'trip_num'], how="outer", indicator=True)
    result_df = result_df[result_df['_merge'] == 'both']
    result_df['delay'].replace(np.nan, 0, inplace=True)

    print(result_df[result_df['delay'] != 0])
