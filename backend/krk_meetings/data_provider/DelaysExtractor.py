import pandas as pd


class DelaysExtractor:
    def extract(self, vehicle_positions_df: pd.DataFrame, stop_times_df: pd.DataFrame) -> pd.DataFrame:
        vehicle_positions_df.set_index(['service_id', 'block_id', 'trip_num', 'stop_sequence'], inplace=True)
        delays_df = vehicle_positions_df.join(stop_times_df)
        delays_df = delays_df.dropna()
        delays_df['delay'] = (delays_df['timestamp'] - delays_df['departure_time'] + 3600) % (3600 * 24)
        delays_df['delay'] = delays_df['delay'].apply(
            lambda delay: delay if delay < 12 * 3600 else delay - 24 * 3600)
        delays_df = delays_df[delays_df['delay'] > -600]
        delays_df.reset_index(['stop_sequence'], inplace=True)
        delays_df = delays_df[['delay']]
        delays_df['registered'] = True
        return delays_df
