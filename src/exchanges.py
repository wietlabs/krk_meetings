import json
from enum import Enum
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_classes.ConnectionResults import ConnectionResults
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.data_classes.SequenceQuery import SequenceQuery
from src.data_classes.SequenceResults import SequenceResults


class EXCHANGES(Enum):
    FLOYD_DATA = ("DIRECT", "direct", "floyd_data", json.dumps, json.loads)
    CONNECTION_QUERY = ("BASIC", "", "connection_query", json.dumps, ConnectionQuery.from_json)
    CONNECTION_RESULTS = ("BASIC", "", "connection_results_", ConnectionResults.to_json, json.loads)
    MEETING_QUERY = ("BASIC", "", "meeting_query", json.dumps, MeetingQuery.from_json)
    MEETING_RESULTS = ("BASIC", "", "meeting_results_", MeetingResults.to_json, json.loads)
    SEQUENCE_QUERY = ("BASIC", "", "sequence_query", json.dumps, SequenceQuery.from_json)
    SEQUENCE_RESULTS = ("BASIC", "", "sequence_results_", SequenceResults.to_json, json.loads)
