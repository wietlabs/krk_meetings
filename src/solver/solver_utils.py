from datetime import datetime
from src.config import WALKING_ROUTE_ID, DATETIME_FORMAT


def get_stop_id_by_name(stop_name, stops_df_by_name):
    try:
        return int(stops_df_by_name.at[stop_name, 'stop_id'])
    except KeyError:
        return None


def get_stop_name_by_id(stop_id, stops_df):
    return stops_df.at[stop_id, 'stop_name']


def get_route_name_by_id(route_id, routes_df):
    return routes_df.at[route_id, 'route_name']


def get_headsign_by_id(route_id, routes_df):
    return routes_df.at[route_id, 'headsign']


def parse_transfers(transfer, stops_df, routes_df, routes_to_stops_dict):
    result = dict()
    result['start_stop'] = stops_df.at[transfer['start_stop_id'], 'stop_name']
    result['end_stop'] = stops_df.at[transfer['end_stop_id'], 'stop_name']
    if transfer['route_id'] != WALKING_ROUTE_ID:
        result['type'] = 'transfer'
        result['start_datetime'] = transfer['start_datetime']
        result['end_datetime'] = transfer['end_datetime']
        result['route_name'] = routes_df.at[transfer['route_id'], 'route_name']
        result['headsign'] = routes_df.at[transfer['route_id'], 'headsign']
        result['stops'] = get_stop_list(transfer['route_id'], transfer['start_stop_id'],
                                                    transfer['end_stop_id'], stops_df, routes_to_stops_dict)
    else:
        result['type'] = 'walking'
        duration = datetime.strptime(transfer['end_datetime'], DATETIME_FORMAT) - \
                   datetime.strptime(transfer['start_datetime'], DATETIME_FORMAT)
        result['duration_in_minutes'] = int(duration.seconds / 60)
    return result


def get_stop_list(route_id, start_stop_id, end_stop_id, stops_df, routes_to_stops_dict):
    stop_ids_list = routes_to_stops_dict[route_id]
    print(start_stop_id)
    print(end_stop_id)
    print(stop_ids_list)
    print("*" * 50)
    stops = []
    for stop_id in stop_ids_list:
        if stop_id == start_stop_id:
            stops = [start_stop_id]
        elif stops:
            stops.append(stop_id)
            if stop_id == end_stop_id:
                break
    stops = list(map(lambda s:
                     {
                         'name': stops_df.at[s, 'stop_name'],
                         'latitude': stops_df.at[s, 'stop_lat'],
                         'longitude': stops_df.at[s, 'stop_lon'],
                     }, stops))
    return stops
