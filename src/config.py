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


class EXCHANGES(Enum):
    FLOYD_DATA = ("DIRECT", "direct", "floyd_data", json.dumps, json.loads)
    CONNECTION_QUERY = ("BASIC", "", "connection_query", ConnectionQuery.to_json, ConnectionQuery.from_json)
    CONNECTION_RESULTS = ("BASIC", "", "connection_results", ConnectionResults.to_json, ConnectionResults.from_json)
    MEETING_QUERY = ("BASIC", "", "meeting_query", MeetingQuery.to_json, MeetingQuery.from_json)
    MEETING_RESULTS = ("BASIC", "", "meeting_results", MeetingResults.to_json, MeetingResults.from_json)
    SEQUENCE_QUERY = ("BASIC", "", "sequence_query", SequenceQuery.to_json, SequenceQuery.from_json)
    SEQUENCE_RESULTS = ("BASIC", "", "sequence_results", SequenceResults.to_json, SequenceResults.from_json)
