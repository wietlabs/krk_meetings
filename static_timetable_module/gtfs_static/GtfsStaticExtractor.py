import pandas as pd
from pathlib import Path
from GtfsStaticParser import GtfsStaticParser
from GtfsStaticParsedData import GtfsStaticParsedData
from GtfsStaticExtractedData import GtfsStaticExtractedData


class GtfsStaticExtractor:
    def __init__(self):
        # configuration goes here
        pass

    def extract(self, parsed_data: GtfsStaticParsedData):
        stops_df = parsed_data.stops_df
        transfers_df = parsed_data.transfers_df
        stop_times_df = parsed_data.stop_times_df
        trips_df = parsed_data.trips_df

        transfers_trips_df = self.create_transfers_trips_df(transfers_df, trips_df)
        stop_times_trips_df = self.create_stop_times_trips_df_for_service_id(stop_times_df, trips_df)
        avg_durations_df = self.create_avg_durations_df(transfers_df)
        frequency_df = self.create_frequency_df(transfers_df)

        return GtfsStaticExtractedData(stops_df, transfers_trips_df, stop_times_trips_df, avg_durations_df, frequency_df)

    def create_transfers_trips_df(self, transfers_df: pd.DataFrame, trips_df: pd.DataFrame) -> pd.DataFrame:
        df = transfers_df.join(trips_df, on=['service_id', 'block_id', 'trip_num'])
        df = df[['route_id', 'block_id', 'trip_num', 'service_id', 'start_time', 'end_time', 'start_stop_id', 'end_stop_id', 'duration']]
        return df

    def create_stop_times_trips_df_for_service_id(self, stop_times_df: pd.DataFrame, trips_df: pd.DataFrame) -> pd.DataFrame:
        df = stop_times_df.join(trips_df, on=['service_id', 'block_id', 'trip_num'])
        df = df[['stop_id', 'peron_id', 'departure_time', 'route_id']]
        return df

    def create_avg_durations_df(self, transfers_df: pd.DataFrame) -> pd.DataFrame:
        return transfers_df[['start_stop_id', 'end_stop_id', 'duration']].groupby(['start_stop_id', 'end_stop_id']).mean()

    def create_frequency_df(self, stop_times_df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame()
        # stop_times_df = stop_times_df.reset_index()
        # routes_df = pd.read_pickle('tmp/routes_df.pkl').reset_index()
        # df = pd.merge(stop_times_df, routes_df, on=['block_id', 'service_id'])
        # is_first = df['stop_sequence'] == 1
        # df = df[is_first]
        # df = df[['route_id', 'stop_id', 'departure_time']]
        # df = df.groupby(['route_id', 'stop_id']).agg({'departure_time': ['count', 'min', 'max']})
        # df.columns = ['mean', 'min', 'max']
        # df['frequency'] = ((df['max'] - df['min']) / df['mean']).astype(int)
        # df = df.reset_index()
        # df = df[['route_id', 'stop_id', 'frequency']]
        # return df


if __name__ == '__main__':
    parsed_data = GtfsStaticParsedData.load(Path(__file__).parent / 'tmp' / 'parsed_data.pickle')
    extractor = GtfsStaticExtractor()
    extracted_data = extractor.extract(parsed_data)
    extracted_data.save(Path(__file__).parent / 'tmp' / 'extracted_data.pickle')
    print(extracted_data)
