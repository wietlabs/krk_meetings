import pandas as pd
from src.config import FloydDataPaths, MAX_WALKING_DISTANCE
from src.data_provider.utils import get_walking_distance
import openrouteservice
from openrouteservice.directions import directions
from src.utils import save_pickle, load_pickle
import time

openrouteservice_api_key = ''  # Specify your personal API key


def reparse_walking_distances():
    client = openrouteservice.Client(key=openrouteservice_api_key)
    stops_df: pd.DataFrame = pd.read_pickle(FloydDataPaths.stops_df.value)
    stops_df = stops_df[['stop_name', 'stop_lon', 'stop_lat']]
    walking_distances_pickle = load_pickle(FloydDataPaths.api_walking_distances.value)
    api_walking_distances = walking_distances_pickle['distances']
    api_stop_list = stops_df['stop_name'].to_list()
    print(api_stop_list)

    def adjacent_stops_generator():
        for id_1, name_1, lon_1, lat_1 in stops_df.itertuples():
            for id_2, name_2, lon_2, lat_2 in stops_df.itertuples():
                if id_1 < id_2 and get_walking_distance(lon_1, lat_1, lon_2, lat_2) < MAX_WALKING_DISTANCE:
                    yield name_1, lon_1, lat_1, name_2, lon_2, lat_2

    adjacent_stops = list(adjacent_stops_generator())
    all_stops = len(adjacent_stops)
    current_stop_percent = 0
    loop_counter = 0
    for name_1, lon_1, lat_1, name_2, lon_2, lat_2 in adjacent_stops:
        loop_counter += 1
        if 100 * loop_counter / all_stops >= current_stop_percent:
            print(f"{current_stop_percent}% done ")
            current_stop_percent += 1
        if (name_1, name_2) in api_walking_distances.keys():
            continue
        time.sleep(2)
        coords = ((lon_1, lat_1), (lon_2, lat_2))
        if (lon_1, lat_1) == (lon_2, lat_2):
            api_walking_distances[(name_1, name_2)] = 0
            api_walking_distances[(name_2, name_1)] = 0
        else:
            try:
                routes = directions(client, coords, profile='foot-walking')
                api_walking_distances[(name_1, name_2)] = routes['routes'][0]['summary']['duration']
                api_walking_distances[(name_2, name_1)] = routes['routes'][0]['summary']['duration']

            except openrouteservice.exceptions.ApiError:
                break
    save_pickle({'distances': api_walking_distances, 'stop_list': list(api_stop_list)}, FloydDataPaths.api_walking_distances.value)


if __name__ == "__main__":
    # save_pickle({'distances': {}, 'stop_list': []}, FloydDataPaths.api_walking_distances.value)
    reparse_walking_distances()

