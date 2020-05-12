import pandas as pd
from pathlib import Path
from static_timetable_module.gtfs_static.Parser import Parser
from static_timetable_module.gtfs_static.ParsedData import ParsedData
from static_timetable_module.gtfs_static.ExtractedData import ExtractedData


class Extractor:
    def __init__(self):
        # configuration goes here
        pass

    def extract(self, parsed_data: ParsedData):
        stops_df = parsed_data.stops_df
        transfers_df = parsed_data.transfers_df
        stop_times_df = parsed_data.stop_times_df
        trips_df = parsed_data.trips_df

        transfers_trips_df = self.create_transfers_trips_df(transfers_df, trips_df)
        stop_times_trips_df = self.create_stop_times_trips_df_for_service_id(stop_times_df, trips_df)
        avg_durations_df = self.create_avg_durations_df(transfers_df)
        period_df = self.create_period_df(stop_times_df, trips_df)
        first_stops_df = self.create_first_stops_df(stop_times_df, trips_df)
        extended_stops_df = self.extend_stops_df(transfers_df, first_stops_df, stops_df)
        return ExtractedData(extended_stops_df, transfers_trips_df, stop_times_trips_df, avg_durations_df, period_df, first_stops_df)

    def create_transfers_trips_df(self, transfers_df: pd.DataFrame, trips_df: pd.DataFrame) -> pd.DataFrame:
        df = transfers_df.join(trips_df, on=['service_id', 'block_id', 'trip_num'])
        df = df[['route_id', 'block_id', 'trip_num', 'service_id', 'start_time', 'end_time', 'start_stop_id', 'end_stop_id', 'duration', 'stop_sequence']]
        return df

    def create_stop_times_trips_df_for_service_id(self, stop_times_df: pd.DataFrame, trips_df: pd.DataFrame) -> pd.DataFrame:
        df = stop_times_df.join(trips_df, on=['service_id', 'block_id', 'trip_num'])
        df = df[['stop_id', 'peron_id', 'departure_time', 'route_id']]
        return df

    def create_avg_durations_df(self, transfers_df: pd.DataFrame) -> pd.DataFrame:
        return transfers_df[['start_stop_id', 'end_stop_id', 'duration']].groupby(['start_stop_id', 'end_stop_id']).mean()

    def create_period_df(self, stop_times_df: pd.DataFrame, trips_df: pd.DataFrame) -> pd.DataFrame:
        stop_times_df = stop_times_df.reset_index()
        df = stop_times_df.join(trips_df, on=['service_id', 'block_id', 'trip_num'])
        is_first = df['stop_sequence'] == 1
        df = df[is_first]
        df = df[['route_id', 'departure_time']]
        df = df.groupby(['route_id']).agg({'departure_time': ['count', 'min', 'max']})
        df.columns = ['count', 'min', 'max']
        df['period'] = ((df['max'] - df['min']) / df['count'] * 2).astype(int)
        df = df.reset_index()
        df = df[['route_id', 'period']]
        # df = df.set_index('route_id')
        return df

    def create_first_stops_df(self, stop_times_df: pd.DataFrame, trips_df: pd.DataFrame) -> pd.DataFrame:
        stop_times_df = stop_times_df.reset_index()
        df = pd.merge(stop_times_df, trips_df, on=['block_id', 'service_id'])
        is_first = df['stop_sequence'] == 1
        df = df[is_first]
        df = df.drop_duplicates(['stop_id', 'route_id']).reset_index()
        df = df[['stop_id', 'route_id']]
        return df

    def extend_stops_df(self, transfer_df: pd.DataFrame, first_stops_df: pd.DataFrame, stops_df: pd.DataFrame):
        first_stops_df = first_stops_df[['stop_id']]
        first_stops_df = first_stops_df.drop_duplicates('stop_id')
        hubs_df = transfer_df[['start_stop_id', 'end_stop_id']]
        hubs_df = hubs_df.drop_duplicates(subset=['start_stop_id', 'end_stop_id'])
        hubs_df = hubs_df.groupby('start_stop_id').count()
        has_3_neighbours = hubs_df['end_stop_id'] > 2
        start_hubs_df = hubs_df.reset_index().merge(first_stops_df, left_on='start_stop_id', right_on='stop_id')
        start_hubs_df = start_hubs_df[['start_stop_id', 'end_stop_id']].set_index('start_stop_id')
        has_2_neighbours = start_hubs_df['end_stop_id'] > 1
        hubs_3_df = hubs_df[has_3_neighbours]
        hubs_2_df = start_hubs_df[has_2_neighbours]
        hubs_df = hubs_2_df.append(hubs_3_df)
        hubs_df = hubs_df.reset_index()
        hubs_df['stop_id'] = hubs_df['start_stop_id']

        stops_df = stops_df.reset_index()
        stops_df['hub'] = stops_df.apply(lambda row: row.stop_id in set(hubs_df['stop_id']), axis=1)
        stops_df = stops_df.set_index('stop_id')

        return stops_df

if __name__ == '__main__':
    parsed_data = ParsedData.load(Path(__file__).parent / 'tmp' / 'parsed_data.pickle')
    extractor = Extractor()
    stops_df = parsed_data.stops_df
    transfers_df = parsed_data.transfers_df
    stop_times_df = parsed_data.stop_times_df
    trips_df = parsed_data.trips_df
    period_df = extractor.create_period_df(stop_times_df, trips_df)
    is_583 = period_df['route_id'] == 583
    period_df = period_df[is_583]
    period_df = period_df.set_index('route_id')
    r_583 = int(period_df.loc[[583]]['period'])
    print(r_583)
