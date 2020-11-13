from src.data_classes.Walk import Walk


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


def get_stop_list(route_id, start_stop_id, end_stop_id, stops_df, routes_to_stops_dict):
    stop_ids_list = routes_to_stops_dict[route_id]
    stops = []
    for stop_id in stop_ids_list:
        if stop_id == start_stop_id:
            stops = [start_stop_id]
        elif stops:
            stops.append(stop_id)
            if stop_id == end_stop_id:
                break
    stops = [stop_data(stop, stops_df) for stop in stops]
    return stops


def stop_data(stop_id, stops_df):
    return {
        'name': stops_df.at[stop_id, 'stop_name'],
        'latitude': stops_df.at[stop_id, 'stop_lat'],
        'longitude': stops_df.at[stop_id, 'stop_lon'],
    }


def get_connection_data(a_list):
    if len(a_list) == 1 and type(a_list[0]) == Walk:
        walking_only = True
        start_stop_name = None
        end_stop_name = None
        start_datetime = None
        end_datetime = None
    else:
        walking_only = False
        start_stop_name = a_list[0].start_stop_name if type(a_list[0]) != Walk else a_list[1].start_stop_name
        end_stop_name = a_list[-1].end_stop_name if type(a_list[-1]) != Walk else a_list[-2].end_stop_name
        start_datetime = a_list[0].start_datetime if type(a_list[0]) != Walk else a_list[1].start_datetime
        end_datetime = a_list[-1].end_datetime if type(a_list[-1]) != Walk else a_list[-2].end_datetime
    return walking_only, start_stop_name, end_stop_name, start_datetime, end_datetime
