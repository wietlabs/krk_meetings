from datetime import datetime


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


def get_services(s_datetime: datetime, day_to_services_dict: dict, exception_days_dict: dict):
    s_day = s_datetime.weekday()
    s_date = s_datetime.date()
    services = day_to_services_dict[s_day]
    if s_date in exception_days_dict:
        services += exception_days_dict[s_date]["services_to_add"]
        services = [s for s in services if s not in exception_days_dict[s_date]["services_to_remove"]]
    return services
