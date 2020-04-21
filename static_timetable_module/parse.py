import pandas as pd
import utils
from typing import Tuple


class GtfsStaticData:  # server has reference to its instance
    pass


class GtfsStaticParser:
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
        df.set_index(['block_id', 'trip_num', 'service_id'], inplace=True)
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
        df.set_index(['block_id', 'trip_num', 'service_id', 'stop_sequence'], inplace=True)
        df = df[['stop_id', 'peron_id', 'departure_time']]
        return df

    def create_transfers_df(self, stop_times_df: pd.DataFrame) -> pd.DataFrame:
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

    def create_avg_durations_df(self, transfers_df: pd.DataFrame) -> pd.DataFrame:
        return transfers_df[['start_stop_id', 'end_stop_id', 'duration']].groupby(['start_stop_id', 'end_stop_id']).mean()

if __name__ == '__main__':
    calendar_txt_path = r'GTFS_KRK_A/calendar.txt'
    routes_txt_path = r'GTFS_KRK_A/routes.txt'
    trips_txt_path = r'GTFS_KRK_A/trips.txt'
    stops_txt_path = r'GTFS_KRK_A/stops.txt'
    stop_times_txt_path = r'GTFS_KRK_A/stop_times.txt'

    parser = GtfsStaticParser()

    calendar_df = parser.parse_calendar_df(calendar_txt_path)
    calendar_df.to_pickle('tmp/calendar_df.pkl')
    print(calendar_df)

    routes_df = parser.parse_routes_df(routes_txt_path)
    routes_df.to_pickle('tmp/routes_df.pkl')
    print(routes_df)

    trips_df = parser.parse_trips_df(trips_txt_path)
    trips_df.to_pickle('tmp/trips_df.pkl')
    print(trips_df)

    stops_df, perons_df = parser.parse_stops_df(stops_txt_path)
    stops_df.to_pickle('tmp/stops_df.pkl')
    perons_df.to_pickle('tmp/perons_df.pkl')
    print(stops_df)
    print(perons_df)

    stop_times_df = parser.parse_stop_times_df(stop_times_txt_path)
    stop_times_df.to_pickle('tmp/stop_times_df.pkl')
    print(stop_times_df)

    transfers_df = parser.create_transfers_df(stop_times_df)
    transfers_df.to_pickle('tmp/transfers_df.pkl')
    print(transfers_df)

    avg_durations_df = parser.create_avg_durations_df(transfers_df)
    avg_durations_df.to_pickle('tmp/avg_durations_df.pkl')
    print(avg_durations_df)
