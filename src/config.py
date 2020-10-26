from enum import Enum
from pathlib import Path

FLOYD_SOLVER_SEARCHING_TIME: int = 8 * 3600
FLOYD_SOLVER_NUMBER_OF_CONNECTIONS = 25
FLOYD_SOLVER_MAX_PRIORITY_MULTIPLIER: float = 1.5
FLOYD_SOLVER_MAX_PATHS: int = 10
FLOYD_EXTRACTOR_PERIOD_MULTIPLIER: float = 0.5
MAX_WALKING_TIME_IN_MINUTES: float = 10
WALKING_SPEED: float = 1.0
WALKING_ROUTE_ID: int = -1
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

FLOYD_DATA_DIR_PATH = Path(__file__).parent / 'data'
CONFIG_JSON_PATH = Path(__file__).parent / 'data' / 'config.json'


class FloydDataPaths(Enum):
    floyd_graph = FLOYD_DATA_DIR_PATH / "floyd_graph.pickle"
    kernelized_floyd_graph = FLOYD_DATA_DIR_PATH / "kernelized_floyd_graph.pickle"
    distances = FLOYD_DATA_DIR_PATH / "distances.pickle"
    day_to_services_dict = FLOYD_DATA_DIR_PATH / "day_to_services_dict.pickle"
    stop_times_0_dict = FLOYD_DATA_DIR_PATH / "stop_times_0_dict.pickle"
    stop_times_24_dict = FLOYD_DATA_DIR_PATH / "stop_times_24_dict.pickle"
    routes_to_stops_dict = FLOYD_DATA_DIR_PATH / "routes_to_stops_dict.pickle"
    adjacent_stops = FLOYD_DATA_DIR_PATH / "adjacent_stops.pickle"
    stops_df = FLOYD_DATA_DIR_PATH / "stops_df.pickle"
    routes_df = FLOYD_DATA_DIR_PATH / "routes_df.pickle"
    stops_df_by_name = FLOYD_DATA_DIR_PATH / "stops_df_by_name.pickle"


LOCALHOST_ADDRESS = "http://127.0.0.1:5000/"


class URL(Enum):
    CONNECTION = "http://127.0.0.1:5000/connection"
    MEETING = "http://127.0.0.1:5000/meeting"
    SEQUENCE = "http://127.0.0.1:5000/sequence"
    RESULTS = "http://127.0.0.1:5000/result/{}"
    STOPS = "http://127.0.0.1:5000/stops"



class SolverStatusCodes(Enum):
    OK = ""
    BAD_START_STOP_NAME = "Error: Bad start stop name."
    BAD_END_STOP_NAME = "Error: Bad end stop name."
