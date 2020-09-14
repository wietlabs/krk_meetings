import pandas as pd


class Extractor:
    def __init__(self):
        # configuration goes here
        pass

    @staticmethod
    def get_day_to_services_dict(calendar_df: pd.DataFrame):
        day_to_services = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        for service_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday in calendar_df.itertuples():
            if monday: day_to_services[0].append(service_id)
            if tuesday: day_to_services[1].append(service_id)
            if wednesday: day_to_services[2].append(service_id)
            if thursday: day_to_services[3].append(service_id)
            if friday: day_to_services[4].append(service_id)
            if saturday: day_to_services[5].append(service_id)
            if sunday: day_to_services[6].append(service_id)
        return day_to_services

    @staticmethod
    def get_services_list(calendar_df):
        services = []
        for service_id, _, _, _, _, _, _, _ in calendar_df.itertuples():
            services.append(service_id)
        return services

    @staticmethod
    def create_route_ids_df(stop_times_df):
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

    @staticmethod
    def create_routes_trips_df(trips_df, routes_df, routes_ids_df):
        routes_df = trips_df.reset_index().merge(routes_df, on='route_id')[
            ['service_id', 'block_id', 'trip_num', 'trip_headsign', 'route_short_name']]
        routes_df = routes_df.rename(columns={'route_short_name': 'route_name', 'trip_headsign': 'headsign'})
        routes_df = routes_df.set_index(['service_id', 'block_id', 'trip_num'])
        routes_df = routes_df.join(routes_ids_df).drop_duplicates('route_id')
        routes_df = routes_df.set_index('route_id')[['route_name', 'headsign']]
        return routes_df

    @staticmethod
    def create_transfers_trips_df(transfers_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> pd.DataFrame:
        df = transfers_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df = df[['route_id', 'block_id', 'trip_num', 'service_id', 'start_time', 'end_time', 'start_stop_id', 'end_stop_id', 'duration']]
        return df

    @staticmethod
    def create_stop_times_trips_df_for_service_id(stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> pd.DataFrame:
        df = stop_times_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df = df[['stop_id', 'peron_id', 'departure_time', 'route_id']]
        return df

    @staticmethod
    def create_avg_durations_df(transfers_df: pd.DataFrame) -> pd.DataFrame:
        return transfers_df[['start_stop_id', 'end_stop_id', 'duration']].groupby(['start_stop_id', 'end_stop_id']).mean()

    # TODO HOW TO CALCULATE PERIOD?
    # TODO for now we return 24 * 3600 / count
    @staticmethod
    def create_period_df(stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> pd.DataFrame:
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

    @staticmethod
    def set_first_and_last_stop(stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame, stops_df: pd.DataFrame) -> pd.DataFrame:
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

    @staticmethod
    def extend_stops_df(transfer_df: pd.DataFrame, stops_df: pd.DataFrame):
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

    @staticmethod
    def create_route_to_stops_dict(stop_times_df: pd.DataFrame, route_ids_df: pd.DataFrame) -> dict:
        stop_times_df = stop_times_df.reset_index()
        df = stop_times_df.join(route_ids_df, on=['block_id', 'trip_num', 'service_id'])
        df.drop_duplicates(subset=['route_id', 'stop_sequence'], inplace=True)
        df = df[['route_id', 'stop_sequence', 'stop_id', 'peron_id']]
        df.sort_values('stop_sequence', inplace=True, ascending=False)
        route_to_stops_dict = {}
        for _, route_id, stop_sequence, stop_id, peron_id in df.itertuples():
            if route_id not in route_to_stops_dict:
                route_to_stops_dict[route_id] = []
            route_to_stops_dict[route_id].append(stop_id)
        return route_to_stops_dict
