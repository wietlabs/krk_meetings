from enum import Enum

from src.data_classes.FloydSolverData import FloydSolverData
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_classes.ConnectionResults import ConnectionResults

FLOYD_SOLVER_SEARCHING_TIME = 8 * 3600
FLOYD_SOLVER_MAX_PRIORITY_MULTIPLIER = 1.5
FLOYD_SOLVER_MAX_PATHS = 10
FLOYD_EXTRACTOR_PERIOD_MULTIPLIER = 0.5


class EXCHANGES(Enum):
    FLOYD_DATA = ("DIRECT", "direct", "floyd_data", FloydSolverData.to_json, FloydSolverData.from_json)
    CONNECTION_QUERY = ("BASIC", "", "connection_query", ConnectionQuery.to_json, ConnectionQuery.from_json)
    CONNECTION_RESULTS = ("BASIC", "", "connection_results", ConnectionResults.list_to_json, ConnectionResults.list_from_json)
