from typing import Tuple

import pandas as pd
from matplotlib.path import Path

from src.data_classes.ParsedData import ParsedData
from src.data_provider.utils import parse_service_id, parse_route_id, parse_trip_id, parse_stop_id, parse_time


class Parser:
    def parse(self, gtfs_dir_path: Path):
        calendar_df = self.parse_calendar_df(gtfs_dir_path / 'calendar.txt')
        routes_df = self.parse_routes_df(gtfs_dir_path / 'routes.txt')
        trips_df = self.parse_trips_df(gtfs_dir_path / 'trips.txt')
        stops_df, perons_df = self.parse_stops_df(gtfs_dir_path / 'stops.txt')
        stop_times_df = self.parse_stop_times_df(gtfs_dir_path / 'stop_times.txt')

        transfers_df = self.create_transfers_df(stop_times_df)

        return ParsedData(calendar_df, routes_df, trips_df, stops_df, perons_df, stop_times_df, transfers_df)

    def parse_calendar_df(self, calendar_txt_path: Path) -> pd.DataFrame:
        df = pd.read_csv(calendar_txt_path, usecols=['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
        df['service_id'] = df['service_id'].map(parse_service_id)
        df.set_index('service_id', inplace=True)
        return df

    def parse_routes_df(self, routes_txt_path: Path) -> pd.DataFrame:
        df = pd.read_csv(routes_txt_path, usecols=['route_id', 'route_short_name'], dtype={'route_short_name': 'str'})
        df['route_id'] = df['route_id'].map(parse_route_id)
        df.set_index('route_id', inplace=True)
        return df

    def parse_trips_df(self, trips_txt_path: Path) -> pd.DataFrame:
        df = pd.read_csv(trips_txt_path, usecols=['trip_id', 'route_id', 'trip_headsign'])
        df['block_id'], df['trip_num'], df['service_id'] = zip(*df['trip_id'].map(parse_trip_id))  # TODO: consider df.apply
        df.drop(columns=['trip_id'], inplace=True)
        df['route_id'] = df['route_id'].map(parse_route_id)
        df.set_index(['service_id', 'block_id', 'trip_num'], inplace=True)
        return df

    def parse_stops_df(self, stops_txt_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = pd.read_csv(stops_txt_path, usecols=['stop_id', 'stop_name', 'stop_lat', 'stop_lon'])
        df['stop_id'], df['peron_id'] = zip(*df['stop_id'].map(parse_stop_id))  # TODO: consider df.apply
        perons_df = df.set_index('peron_id')
        perons_df.columns = ['stop_id', 'peron_name', 'peron_lat', 'peron_lon']
        stops_df = df[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']] \
                    .groupby(['stop_id', 'stop_name'], as_index=False) \
                    .mean() \
                    .set_index('stop_id')
        return stops_df, perons_df

    def parse_stop_times_df(self, stop_times_txt_path: Path) -> pd.DataFrame:
        df = pd.read_csv(stop_times_txt_path, usecols=['trip_id', 'departure_time', 'stop_id', 'stop_sequence'])
        df['block_id'], df['trip_num'], df['service_id'] = zip(*df['trip_id'].map(parse_trip_id))  # TODO: consider df.apply
        df.drop(columns=['trip_id'], inplace=True)
        df['stop_id'], df['peron_id'] = zip(*df['stop_id'].map(parse_stop_id))  # TODO: consider df.apply
        df['departure_time'] = df['departure_time'].map(parse_time)
        df.set_index(['service_id', 'block_id', 'trip_num', 'stop_sequence'], inplace=True)
        df = df[['stop_id', 'peron_id', 'departure_time']]
        return df

    def create_transfers_df(self, stop_times_df: pd.DataFrame) -> pd.DataFrame:  # TODO: rename create to generate?
        stop_times_df = stop_times_df.reset_index()
        def gen():
            prev_trip_num = None
            for _, service_id, block_id, trip_num, stop_sequence, stop_id, peron_id, departure_time in stop_times_df.itertuples():
                if trip_num == prev_trip_num and block_id == prev_block_id and service_id == prev_service_id:
                    yield block_id, trip_num, service_id, prev_departure_time, departure_time, \
                          prev_stop_id, stop_id, prev_peron_id, peron_id, prev_stop_sequence
                prev_service_id, prev_block_id, prev_trip_num, prev_stop_sequence, \
                    prev_stop_id, prev_peron_id, prev_departure_time = \
                    service_id, block_id, trip_num, stop_sequence, stop_id, peron_id, departure_time

        df = pd.DataFrame(gen(), columns=['block_id', 'trip_num', 'service_id', 'start_time', 'end_time',
                                          'start_stop_id', 'end_stop_id', 'start_peron_id', 'end_peron_id', 'stop_sequence'])
        df['duration'] = df['end_time'] - df['start_time']
        return df
