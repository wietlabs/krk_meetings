from pathlib import Path
from typing import Tuple, Union, IO
from zipfile import ZipFile

import pandas as pd
from pandas._typing import FilePathOrBuffer

from krk_meetings.data_classes.ParsedData import ParsedData
from krk_meetings.data_provider.data_provider_utils import parse_service_id, parse_route_id, parse_trip_id, parse_stop_id, parse_time


class Parser:
    def parse(self, gtfs_zip_path_or_buffer: Union[str, Path, IO]):
        if isinstance(gtfs_zip_path_or_buffer, (str, Path)):
            with open(gtfs_zip_path_or_buffer, 'rb') as f:
                return self._parse_io(f)

        return self._parse_io(gtfs_zip_path_or_buffer)

    def _parse_io(self, gtfs_zip_io: IO):
        with ZipFile(gtfs_zip_io) as zipfile:
            with zipfile.open('calendar.txt') as f:
                calendar_df = self.parse_calendar_df(f)

            try:
                with zipfile.open('calendar_dates.txt') as f:
                    calendar_dates_df = self.parse_calendar_dates_df(f)
            except KeyError:
                calendar_dates_df = pd.DataFrame(columns=['service_id', 'date', 'exception_type'])

            with zipfile.open('routes.txt') as f:
                routes_df = self.parse_routes_df(f)

            with zipfile.open('trips.txt') as f:
                trips_df = self.parse_trips_df(f)

            with zipfile.open('stops.txt') as f:
                stops_df, perons_df = self.parse_stops_df(f)

            with zipfile.open('stop_times.txt') as f:
                stop_times_df = self.parse_stop_times_df(f)

        transfers_df = self.create_transfers_df(stop_times_df)

        return ParsedData(calendar_df=calendar_df,
                          calendar_dates_df=calendar_dates_df,
                          routes_df=routes_df,
                          trips_df=trips_df,
                          stops_df=stops_df,
                          perons_df=perons_df,
                          stop_times_df=stop_times_df,
                          transfers_df=transfers_df)

    def parse_calendar_df(self, calendar_txt: FilePathOrBuffer) -> pd.DataFrame:
        df = pd.read_csv(calendar_txt,
                         usecols=['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
                                  'sunday'])
        df['service_id'] = df['service_id'].map(parse_service_id)
        df.set_index('service_id', inplace=True)
        return df

    def parse_calendar_dates_df(self, calendar_dates_txt: FilePathOrBuffer) -> pd.DataFrame:
        df = pd.read_csv(calendar_dates_txt, usecols=['service_id', 'date', 'exception_type'], parse_dates=['date'])
        df['service_id'] = df['service_id'].map(parse_service_id)
        df['date'] = df['date'].dt.date
        df.sort_values(by=['date', 'exception_type', 'service_id'], inplace=True)
        return df

    def parse_routes_df(self, routes_txt: FilePathOrBuffer) -> pd.DataFrame:
        df = pd.read_csv(routes_txt, usecols=['route_id', 'route_short_name'], dtype={'route_short_name': 'str'})
        df['route_id'] = df['route_id'].map(parse_route_id)
        df.set_index('route_id', inplace=True)
        return df

    def parse_trips_df(self, trips_txt: FilePathOrBuffer) -> pd.DataFrame:
        df = pd.read_csv(trips_txt, usecols=['trip_id', 'route_id', 'trip_headsign'])
        df['block_id'], df['trip_num'], df['service_id'] = zip(
            *df['trip_id'].map(parse_trip_id))  # TODO: consider df.apply
        df.drop(columns=['trip_id'], inplace=True)
        df['route_id'] = df['route_id'].map(parse_route_id)
        df.set_index(['service_id', 'block_id', 'trip_num'], inplace=True)
        return df

    def parse_stops_df(self, stops_txt: FilePathOrBuffer) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = pd.read_csv(stops_txt, usecols=['stop_id', 'stop_name', 'stop_lat', 'stop_lon'])
        df['stop_id'], df['peron_id'] = zip(*df['stop_id'].map(parse_stop_id))  # TODO: consider df.apply
        perons_df = df.set_index('peron_id')
        perons_df.columns = ['stop_id', 'peron_name', 'peron_lat', 'peron_lon']
        stops_df = df[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']] \
            .groupby(['stop_id', 'stop_name'], as_index=False) \
            .mean() \
            .set_index('stop_id')
        return stops_df, perons_df

    def parse_stop_times_df(self, stop_times_txt: FilePathOrBuffer) -> pd.DataFrame:
        df = pd.read_csv(stop_times_txt, usecols=['trip_id', 'departure_time', 'stop_id', 'stop_sequence'])
        df['block_id'], df['trip_num'], df['service_id'] = zip(
            *df['trip_id'].map(parse_trip_id))  # TODO: consider df.apply
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
                                          'start_stop_id', 'end_stop_id', 'start_peron_id', 'end_peron_id',
                                          'stop_sequence'])
        df['duration'] = df['end_time'] - df['start_time']
        return df
