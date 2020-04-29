import pandas as pd
from abc import ABC
from pathlib import Path
from typing import Tuple
import utils
from ParsedData import ParsedData


class Parser:
    def __init__(self):
        # configuration goes here
        pass

    def parse(self, gtfs_dir: str):
        calendar_df = self.parse_calendar_df(gtfs_dir / 'calendar.txt')
        routes_df = self.parse_routes_df(gtfs_dir / 'routes.txt')
        trips_df = self.parse_trips_df(gtfs_dir / 'trips.txt')
        stops_df, perons_df = self.parse_stops_df(gtfs_dir / 'stops.txt')
        stop_times_df = self.parse_stop_times_df(gtfs_dir / 'stop_times.txt')

        transfers_df = self.create_transfers_df(stop_times_df)

        return ParsedData(calendar_df, routes_df, trips_df, stops_df, perons_df, stop_times_df, transfers_df)

    def parse_calendar_df(self, calendar_txt_path: str) -> pd.DataFrame:
        df = pd.read_csv(calendar_txt_path, usecols=['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
        df['service_id'] = df['service_id'].map(utils.parse_service_id)
        df.set_index('service_id', inplace=True)
        return df

    def parse_routes_df(self, routes_txt_path: str) -> pd.DataFrame:
        df = pd.read_csv(routes_txt_path, usecols=['route_id', 'route_short_name'], dtype={'route_short_name': 'str'})
        df['route_id'] = df['route_id'].map(utils.parse_route_id)
        df.set_index('route_id', inplace=True)
        return df

    def parse_trips_df(self, trips_txt_path: str) -> pd.DataFrame:
        df = pd.read_csv(trips_txt_path, usecols=['trip_id', 'route_id', 'trip_headsign'])
        df['block_id'], df['trip_num'], df['service_id'] = zip(*df['trip_id'].map(utils.parse_trip_id))  # TODO: consider df.apply
        df.drop(columns=['trip_id'], inplace=True)
        df['route_id'] = df['route_id'].map(utils.parse_route_id)
        df.set_index(['service_id', 'block_id', 'trip_num'], inplace=True)
        return df

    def parse_stops_df(self, stops_txt_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = pd.read_csv(stops_txt_path, usecols=['stop_id', 'stop_name', 'stop_lat', 'stop_lon'])
        df['stop_id'], df['peron_id'] = zip(*df['stop_id'].map(utils.parse_stop_id))  # TODO: consider df.apply
        perons_df = df.set_index('peron_id')
        stops_df = df[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']] \
                    .groupby(['stop_id', 'stop_name'], as_index=False) \
                    .mean() \
                    .set_index('stop_id')
        return stops_df, perons_df

    def parse_stop_times_df(self, stop_times_txt_path: str) -> pd.DataFrame:
        df = pd.read_csv(stop_times_txt_path, usecols=['trip_id', 'departure_time', 'stop_id', 'stop_sequence'])
        df['block_id'], df['trip_num'], df['service_id'] = zip(*df['trip_id'].map(utils.parse_trip_id))  # TODO: consider df.apply
        df.drop(columns=['trip_id'], inplace=True)
        df['stop_id'], df['peron_id'] = zip(*df['stop_id'].map(utils.parse_stop_id))  # TODO: consider df.apply
        df['departure_time'] = df['departure_time'].map(utils.parse_time)
        df.set_index(['service_id', 'block_id', 'trip_num', 'stop_sequence'], inplace=True)
        df = df[['stop_id', 'peron_id', 'departure_time']]
        return df

    def create_transfers_df(self, stop_times_df: pd.DataFrame) -> pd.DataFrame:  # TODO: rename create to generate?
        stop_times_df = stop_times_df.reset_index()
        def gen():
            start = {'trip_num': None}  # TODO: assign first row
            for _, end in stop_times_df.iterrows():
                if start['trip_num'] == end['trip_num'] and start['block_id'] == end['block_id'] and start['service_id'] == end['service_id']:
                    yield start['block_id'], start['trip_num'], start['service_id'], start['departure_time'], end['departure_time'], \
                          start['stop_id'], end['stop_id'], start['peron_id'], end['peron_id']
                start = end

        df = pd.DataFrame(gen(), columns=['block_id', 'trip_num', 'service_id', 'start_time', 'end_time',
                                          'start_stop_id', 'end_stop_id', 'start_peron_id', 'end_peron_id'])
        df['duration'] = df['end_time'] - df['start_time']
        return df

if __name__ == '__main__':
    parser = Parser()
    parsed_data = parser.parse(Path(__file__).parent / 'GTFS_KRK_A')
    parsed_data.save(Path(__file__).parent / 'tmp' / 'parsed_data.pickle')
    print(parsed_data)
