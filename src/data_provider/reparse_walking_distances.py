import pandas as pd
from src.config import FloydDataPaths, MAX_WALKING_DISTANCE
from src.data_provider.utils import get_walking_distance
import openrouteservice
from openrouteservice.directions import directions
from src.utils import save_pickle
import time


def reparse_walking_distances():
    client = openrouteservice.Client(key='5b3ce3597851110001cf62487bef61f55b514bcaafb033808b4114e6')  # Specify your personal API key
    stops_df: pd.DataFrame = pd.read_pickle(FloydDataPaths.stops_df.value)
    stops_df = stops_df[['stop_name', 'stop_lon', 'stop_lat']]

    def adjacent_stops_generator():
        for id_1, name_1, lon_1, lat_1 in stops_df.itertuples():
            for id_2, name_2, lon_2, lat_2 in stops_df.itertuples():
                if id_1 < id_2 and get_walking_distance(lon_1, lat_1, lon_2, lat_2) < MAX_WALKING_DISTANCE:
                    yield name_1, lon_1, lat_1, name_2, lon_2, lat_2

    api_walking_distances = dict()
    adjacent_stops = list(adjacent_stops_generator())
    all_stops = len(adjacent_stops)
    current_stop_percent = 0
    loop_counter = 0
    for name_1, lon_1, lat_1, name_2, lon_2, lat_2 in adjacent_stops:
        if 100 * loop_counter / all_stops >= current_stop_percent:
            print(f"{current_stop_percent}% done")
            current_stop_percent += 1
        time.sleep(2)
        coords = ((lon_1, lat_1), (lon_2, lat_2))
        if (lon_1, lat_1) == (lon_2, lat_2):
            api_walking_distances[(name_1, name_2)] = 0
        else:
            routes = directions(client, coords, profile='foot-walking')
            api_walking_distances[(name_1, name_2)] = routes['routes'][0]['summary']['duration']
    save_pickle(api_walking_distances, FloydDataPaths.api_walking_distances.value)


if __name__ == "__main__":
    reparse_walking_distances()

