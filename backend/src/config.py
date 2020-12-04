from enum import Enum
from pathlib import Path

from src.data_provider.ExtractorConfiguration import ExtractorConfiguration
from src.solver.ConnectionSolverConfiguration import ConnectionSolverConfiguration


MAX_WALKING_DISTANCE = 1000  # min
WALKING_SPEED: float = 1.0
WALKING_ROUTE_ID: int = -1
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

DEFAULT_FLOYD_EXTRACTOR_CONFIGURATION = ExtractorConfiguration(
    daily_period_multiplier=0.8,
    nightly_period_multiplier=0.4,
    change_penalty=1800,
    nightly_route_ranges=[(600, 699), (900, 999)],
    daily_hours=19,  # from 5 to 24
    nightly_hours=5,  # from 24 to 5
    walking_route_id=WALKING_ROUTE_ID,
    max_walking_time_in_minutes=10
)

DEFAULT_CONNECTION_SOLVER_CONFIGURATION = ConnectionSolverConfiguration(
    max_searching_time=8*3600,  # sec
    partition_time=1800,  # sec
    max_travel_time=4*3600,  # sec
    number_of_connections_returned=25,
    max_priority_multiplier=1.2,
    max_priority_cap=2400,  # sec - cant be 0 due to ban of walking from stop to stop twice in a row
    path_calculation_boost=1.5,
    max_number_of_paths=6,
    max_path_len=6,
    max_path_calculation_time=3,  # sec
    walking_route_id=WALKING_ROUTE_ID,
    walking_index=(WALKING_ROUTE_ID, WALKING_ROUTE_ID, WALKING_ROUTE_ID)
)

FLOYD_DATA_DIR_PATH = Path(__file__).parent / 'data'
CONFIG_JSON_PATH = Path(__file__).parent / 'data' / 'config.json'


class FloydDataPaths(Enum):
    floyd_graph = FLOYD_DATA_DIR_PATH / "floyd_graph.pickle"
    kernelized_floyd_graph = FLOYD_DATA_DIR_PATH / "kernelized_floyd_graph.pickle"
    distances = FLOYD_DATA_DIR_PATH / "distances.pickle"
    day_to_services_dict = FLOYD_DATA_DIR_PATH / "day_to_services_dict.pickle"
    current_stop_times_dict = FLOYD_DATA_DIR_PATH / "current_stop_times_dict.pickle"
    previous_stop_times_dict = FLOYD_DATA_DIR_PATH / "previous_stop_times_dict.pickle"
    next_stop_times_dict = FLOYD_DATA_DIR_PATH / "next_stop_times_dict.pickle"
    routes_to_stops_dict = FLOYD_DATA_DIR_PATH / "routes_to_stops_dict.pickle"
    adjacent_stops = FLOYD_DATA_DIR_PATH / "adjacent_stops.pickle"
    stops_df = FLOYD_DATA_DIR_PATH / "stops_df.pickle"
    routes_df = FLOYD_DATA_DIR_PATH / "routes_df.pickle"
    stops_df_by_name = FLOYD_DATA_DIR_PATH / "stops_df_by_name.pickle"
    api_walking_distances = FLOYD_DATA_DIR_PATH / "api_walking_distances.pickle"
    exception_days = FLOYD_DATA_DIR_PATH / "exception_days.pickle"
    delays_dict = FLOYD_DATA_DIR_PATH / "delays_dict.pickle"
    stops_times_df = FLOYD_DATA_DIR_PATH / "stops_times_df.pickle"
    delays_df = FLOYD_DATA_DIR_PATH / "delays_df.pickle"


class URL(Enum):
    CONNECTION = "http://127.0.0.1:5000/connection"
    MEETING = "http://127.0.0.1:5000/meeting"
    SEQUENCE = "http://127.0.0.1:5000/sequence"
    RESULTS = "http://127.0.0.1:5000/result/{}"
    STOPS = "http://127.0.0.1:5000/stops"


class ErrorCodes(Enum):
    OK = {"error": "OK"}
    BAD_START_STOP_NAME = {"error": "BAD START STOP NAME"}
    BAD_END_STOP_NAME = {"error": "BAD END STOP NAME"}
    BAD_STOP_NAMES_IN_SEQUENCE = {"error": "BAD STOP NAME IN REQUESTED SEQUENCE"}
    BAD_START_STOP_NAMES_IN_MEETING = {"error": "BAD START STOP NAME IN REQUESTED MEETING"}
    BAD_CONNECTION_JSON_FORMAT = {"error": "BAD JSON FORMAT FOR CONNECTION POST"}
    BAD_MEETING_JSON_FORMAT = {"error": "BAD JSON FORMAT FOR MEETING POST"}
    BAD_SEQUENCE_JSON_FORMAT = {"error": "BAD JSON FORMAT FOR SEQUENCE POST"}
    BAD_QUERY_ID_TYPE = {"error": "BAD QUERY ID VALUE TYPE"}
    BAD_QUERY_ID_VALUE = {"error": "BAD QUERY ID VALUE"}
    INTERNAL_SERVER_ERROR = {"error": "INTERNAL SERVER ERROR"}
