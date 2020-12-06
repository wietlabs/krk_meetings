from src.config import FloydDataPaths
import pandas as pd


class DelaysExtractor:
    def extract(self, vehicle_positions_df: pd.DataFrame, data_path=FloydDataPaths) -> pd.DataFrame:
        vehicle_positions_df.set_index(['service_id', 'block_id', 'trip_num', 'stop_sequence'], inplace=True)
        stop_times_df = pd.read_pickle(data_path.stops_times_df.value)
        delays_df = vehicle_positions_df.join(stop_times_df)
        delays_df = delays_df.dropna()
        delays_df['delay'] = delays_df.apply(
            lambda row: (int(row['timestamp'] - row['departure_time'] + 3600) % (3600 * 24)), axis=1)
        delays_df['delay'] = delays_df['delay'].apply(
            lambda delay: delay if delay < 12 * 3600 else delay - 24 * 3600)
        delays_df = delays_df[delays_df['delay'] > -600]
        delays_df.reset_index(['stop_sequence'], inplace=True)
        delays_df = delays_df[['delay']]
        return delays_df
