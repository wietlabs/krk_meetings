from enum import Enum
from pathlib import Path

RESOURCES_DIR_PATH = Path(__file__).parent / 'resources'


class TestFloydDataPaths(Enum):
    floyd_graph = RESOURCES_DIR_PATH / "floyd_graph.pickle"
    kernelized_floyd_graph = RESOURCES_DIR_PATH / "kernelized_floyd_graph.pickle"
    distances = RESOURCES_DIR_PATH / "distances.pickle"
    day_to_services_dict = RESOURCES_DIR_PATH / "day_to_services_dict.pickle"
    stop_times_0_dict = RESOURCES_DIR_PATH / "stop_times_0_dict.pickle"
    stop_times_24_dict = RESOURCES_DIR_PATH / "stop_times_24_dict.pickle"
    routes_to_stops_dict = RESOURCES_DIR_PATH / "routes_to_stops_dict.pickle"
    adjacent_stops = RESOURCES_DIR_PATH / "adjacent_stops.pickle"
    stops_df = RESOURCES_DIR_PATH / "stops_df.pickle"
    routes_df = RESOURCES_DIR_PATH / "routes_df.pickle"
    stops_df_by_name = RESOURCES_DIR_PATH / "stops_df_by_name.pickle"
    api_walking_distances = RESOURCES_DIR_PATH / "api_walking_distances.pickle"
    exception_days = RESOURCES_DIR_PATH / "exception_days.pickle"
