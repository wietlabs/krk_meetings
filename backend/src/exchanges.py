import json
from enum import Enum
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_classes.ConnectionResults import ConnectionResults
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults
from src.data_classes.SequenceQuery import SequenceQuery
from src.data_classes.SequenceResults import SequenceResults


class MESSAGES(Enum):
    DATA_UPDATED = "DATA UPDATED"
    DELAYS_UPDATED = "DELAYS UPDATED"


class EXCHANGES(Enum):
    CONNECTION_DATA_MANAGER = ("TOPIC", "topic", "*", json.dumps, json.loads)
    MEETING_DATA_MANAGER = ("TOPIC", "topic", "data_provider", json.dumps, json.loads)
    SEQUENCE_DATA_MANAGER = ("TOPIC", "topic", "data_provider", json.dumps, json.loads)
    FLASK_DATA_MANAGER = ("TOPIC", "topic", "data_provider", json.dumps, json.loads)
    DATA_PROVIDER = ("TOPIC", "topic", "data_provider", json.dumps, json.loads)
    DELAYS_PROVIDER = ("TOPIC", "topic", "delay_provider", json.dumps, json.loads)

    FLASK_SERVER_CONNECTION = ("BASIC", "", "flask_server_connection", ConnectionResults.to_json, json.loads)
    FLASK_SERVER_MEETING = ("BASIC", "", "flask_server_meeting", MeetingResults.to_json, json.loads)
    FLASK_SERVER_SEQUENCE = ("BASIC", "", "flask_server_sequence", SequenceResults.to_json, json.loads)
    CONNECTION_QUERY = ("BASIC", "", "connection_query", json.dumps, ConnectionQuery.from_json)
    MEETING_QUERY = ("BASIC", "", "meeting_query", json.dumps, MeetingQuery.from_json)
    SEQUENCE_QUERY = ("BASIC", "", "sequence_query", json.dumps, SequenceQuery.from_json)
