from enum import Enum

FLOYD_SOLVER_SEARCHING_TIME: int = 8 * 3600
FLOYD_SOLVER_MAX_PRIORITY_MULTIPLIER: float = 1.5
FLOYD_SOLVER_MAX_PATHS: int = 10
FLOYD_EXTRACTOR_PERIOD_MULTIPLIER: float = 0.5
MAX_WALKING_TIME_IN_MINUTES: float = 10
WALKING_SPEED: float = 1.0
WALKING_ROUTE_ID: int = -1
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"


class URL(Enum):
    CONNECTION = "http://127.0.0.1:5000/connection"
    MEETING = "http://127.0.0.1:5000/meeting"
    SEQUENCE = "http://127.0.0.1:5000/sequence"


class SolverStatusCodes(Enum):
    OK = ""
    BAD_START_STOP_NAME = "Error: Bad start stop name."
    BAD_END_STOP_NAME = "Error: Bad end stop name."
