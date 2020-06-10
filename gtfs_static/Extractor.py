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
        first_stops_df = self.create_first_stops_df(stop_times_df, route_ids_df)
        extended_stops_df = self.extend_stops_df(transfers_df, first_stops_df, stops_df)
        stops_df_by_name = stops_df.reset_index().set_index('stop_name')
        return ExtractedData(extended_stops_df, transfers_route_ids_df, stop_times_route_ids_df, avg_durations_df, period_df, first_stops_df, routes_trips_df, stops_df_by_name)

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
        is_first = df['stop_sequence'] == 1
        df = df[is_first]
        df = df[['route_id', 'departure_time']]
        df = df.groupby(['route_id']).agg({'departure_time': ['count', 'min', 'max']})
        df.columns = ['count', 'min', 'max']
        df['period'] = (24 * 3600 / df['count']).astype(int) * 10 # TODO ONLY FOR NOW
        df = df.reset_index()
        df = df[['route_id', 'period']]
        df = df.set_index('route_id')
        return df

    def create_first_stops_df(self, stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> pd.DataFrame:
        stop_times_df = stop_times_df.reset_index()
        df = pd.merge(stop_times_df, route_ids_df, on=['block_id', 'service_id'])
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
