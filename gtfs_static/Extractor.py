import pandas as pd
from DataClasses.ParsedData import ParsedData
from DataClasses.ExtractedData import ExtractedData


class Extractor:
    def __init__(self):
        # configuration goes here
        pass

    def extract(self, parsed_data: ParsedData):
        stops_df = parsed_data.stops_df
        transfers_df = parsed_data.transfers_df
        stop_times_df = parsed_data.stop_times_df
        trips_df = parsed_data.trips_df
        routes_df = parsed_data.routes_df

        routes_trips_df = self.create_routes_trips_df(trips_df, routes_df)
        route_ids_df = self.create_route_ids_df(stop_times_df)
        transfers_route_ids_df = self.create_transfers_trips_df(transfers_df, route_ids_df)
        stop_times_route_ids_df = self.create_stop_times_trips_df_for_service_id(stop_times_df, route_ids_df)
        avg_durations_df = self.create_avg_durations_df(transfers_df)
        period_df = self.create_period_df(stop_times_df, route_ids_df)
        stops_df = self.set_first_and_last_stop(stop_times_df, route_ids_df, stops_df)
        stops_df = self.extend_stops_df(transfers_df, stops_df)
        stops_df_by_name = stops_df.reset_index().set_index('stop_name')
        return ExtractedData(stops_df, transfers_route_ids_df, stop_times_route_ids_df, avg_durations_df, period_df, routes_trips_df, stops_df_by_name)

    def create_route_ids_df(self, stop_times_df):
        routes_path_df = stop_times_df.groupby(['block_id', 'trip_num', 'service_id']).agg(
            {'peron_id': lambda x: tuple(x)})
        routes_ids_df = routes_path_df.drop_duplicates('peron_id')
        routes_ids_df = routes_ids_df.reset_index()[['peron_id']]
        routes_ids_df = routes_ids_df.reset_index().rename(columns={'index': 'route_id'})
        routes_ids_df = routes_ids_df.set_index('peron_id')
        routes_ids_df = routes_path_df.reset_index().merge(routes_ids_df, on='peron_id')
        routes_ids_df = routes_ids_df[['block_id', 'trip_num', 'service_id', 'route_id']]
        routes_ids_df = routes_ids_df.set_index(['block_id', 'trip_num', 'service_id'])
        return routes_ids_df

    def create_routes_trips_df(self, trips_df, routes_df):
        routes_df = trips_df.reset_index().merge(routes_df, on='route_id')[
            ['service_id', 'block_id', 'trip_num', 'trip_headsign', 'route_short_name']]
        routes_df = routes_df.rename(columns={'route_short_name': 'route_name', 'trip_headsign': 'headsign'})
        return routes_df

    def create_transfers_trips_df(self, transfers_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> pd.DataFrame:
        df = transfers_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df = df[['route_id', 'block_id', 'trip_num', 'service_id', 'start_time', 'end_time', 'start_stop_id', 'end_stop_id', 'duration']]
        return df

    def create_stop_times_trips_df_for_service_id(self, stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> pd.DataFrame:
        df = stop_times_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df = df[['stop_id', 'peron_id', 'departure_time', 'route_id']]
        return df

    def create_avg_durations_df(self, transfers_df: pd.DataFrame) -> pd.DataFrame:
        return transfers_df[['start_stop_id', 'end_stop_id', 'duration']].groupby(['start_stop_id', 'end_stop_id']).mean()

    # TODO HOW TO CALCULATE PERIOD?
    # TODO for now we return 24 * 3600 / count
    def create_period_df(self, stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> pd.DataFrame:
        stop_times_df = stop_times_df.reset_index()
        df = stop_times_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df = df[df['stop_sequence'] == 2]
        df = df[['route_id', 'departure_time']]
        df = df.groupby(['route_id']).agg({'departure_time': ['count', 'min', 'max']})
        df.columns = ['count', 'min', 'max']
        df['period'] = (24 * 3600 / df['count']).astype(int) * 10 # TODO ONLY FOR NOW
        df = df.reset_index()
        df = df[['route_id', 'period']]
        df = df.set_index('route_id')
        return df

    def set_first_and_last_stop(self, stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame, stops_df: pd.DataFrame) -> pd.DataFrame:
        stop_times_df = stop_times_df

        stop_times_df = stop_times_df.join(route_ids_df)
        stop_times_df.sort_values(by='stop_sequence', inplace=True)

        is_first = stop_times_df.drop_duplicates(subset=['route_id'], keep='first')
        is_last = stop_times_df.drop_duplicates(subset=['route_id'], keep='last')
        is_first = is_first['stop_id'].tolist()
        is_last = is_last['stop_id'].tolist()

        stops_df.reset_index(inplace=True)
        stops_df['is_first'] = stops_df['stop_id'].apply(lambda x: x in is_first)
        stops_df['is_last'] = stops_df['stop_id'].apply(lambda x: x in is_last)
        stops_df.set_index('stop_id', inplace=True)
        return stops_df

    def extend_stops_df(self, transfer_df: pd.DataFrame, stops_df: pd.DataFrame):
        hubs_df = transfer_df[['start_stop_id', 'end_stop_id']]
        hubs_df = hubs_df.drop_duplicates(subset=['start_stop_id', 'end_stop_id'])
        hubs_df = hubs_df.groupby('start_stop_id').count()
        hubs_df = stops_df.reset_index().merge(hubs_df, left_on='stop_id', right_on='start_stop_id', how="outer")
        hubs_df.fillna(0, inplace=True)
        hubs_df = hubs_df[['stop_id', 'end_stop_id']].set_index('stop_id')

        def is_hub(row):
            if row['is_first'] and row['is_last']:
                return hubs_df.at[(row['stop_id'], 'end_stop_id')] > 1
            return hubs_df.at[(row['stop_id'], 'end_stop_id')] > 2

        stops_df = stops_df.reset_index()
        stops_df['hub'] = stops_df.apply(is_hub, axis=1)

        stops_df = stops_df.set_index('stop_id')

        return stops_df
