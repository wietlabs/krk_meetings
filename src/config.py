import json
from enum import Enum

from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_classes.ConnectionResults import ConnectionResults
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.data_classes.SequenceQuery import SequenceQuery
from src.data_classes.SequenceResults import SequenceResults

FLOYD_SOLVER_SEARCHING_TIME = 8 * 3600
FLOYD_SOLVER_MAX_PRIORITY_MULTIPLIER = 1.5
FLOYD_SOLVER_MAX_PATHS = 10
FLOYD_EXTRACTOR_PERIOD_MULTIPLIER = 0.5
MAX_WALKING_TIME_IN_MINUTES = 10
WALKING_ROUTE_ID = 0


class EXCHANGES(Enum):
    FLOYD_DATA = ("DIRECT", "direct", "floyd_data", json.dumps, json.loads)
    CONNECTION_QUERY = ("BASIC", "", "connection_query", json.dumps, ConnectionQuery.from_json)
    CONNECTION_RESULTS = ("BASIC", "", "connection_results_", ConnectionResults.to_json, json.loads)
    MEETING_QUERY = ("BASIC", "", "meeting_query", json.dumps, MeetingQuery.from_json)
    MEETING_RESULTS = ("BASIC", "", "meeting_results_", MeetingResults.to_json, json.loads)
    SEQUENCE_QUERY = ("BASIC", "", "sequence_query", json.dumps, SequenceQuery.from_json)
    SEQUENCE_RESULTS = ("BASIC", "", "sequence_results_", SequenceResults.to_json, json.loads)


class URL(Enum):
    CONNECTION = "http://127.0.0.1:5000/connection"
    MEETING = "http://127.0.0.1:5000/meeting"
    SEQUENCE = "http://127.0.0.1:5000/sequence"
