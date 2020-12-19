import json
from dataclasses import dataclass
from enum import Enum
from krk_meetings.data_classes.ConnectionQuery import ConnectionQuery
from krk_meetings.data_classes.ConnectionResults import ConnectionResults
from krk_meetings.data_classes.MeetingQuery import MeetingQuery
from krk_meetings.data_classes.MeetingResults import MeetingResults
from krk_meetings.data_classes.SequenceQuery import SequenceQuery
from krk_meetings.data_classes.SequenceResults import SequenceResults


class MESSAGES(Enum):
    DATA_UPDATED = "DATA UPDATED"
    DELAYS_UPDATED = "DELAYS UPDATED"


class Exchange:
    def __init__(self, exchange_name, exchange_type, routing_key, queue_name, to_json, from_json, separate_instances):
        self.name = exchange_name
        self.type = exchange_type
        self.key = routing_key
        self.queue = queue_name
        self.to_json = to_json
        self.from_json = from_json
        self.separate_instances = separate_instances


class EXCHANGES(Enum):
    CONNECTION_DATA_MANAGER = Exchange("TOPIC", "topic", "*", "connection_data_manager", json.dumps, json.loads, True)
    MEETING_DATA_MANAGER = Exchange("TOPIC", "topic", "data_provider", "meeting_data_manager", json.dumps, json.loads, True)
    SEQUENCE_DATA_MANAGER = Exchange("TOPIC", "topic", "data_provider", "sequence_data_manager", json.dumps, json.loads, True)
    FLASK_DATA_MANAGER = Exchange("TOPIC", "topic", "data_provider", "flask_data_manager", json.dumps, json.loads, True)
    DATA_PROVIDER = Exchange("TOPIC", "topic", "data_provider", "data_provider", json.dumps, json.loads, True)
    DELAYS_PROVIDER = Exchange("TOPIC", "topic", "delay_provider", "delays_provider", json.dumps, json.loads, True)

    FLASK_SERVER_CONNECTION = Exchange("BASIC", "", "flask_server_connection", "flask_server_connection", ConnectionResults.to_json, json.loads, False)
    FLASK_SERVER_MEETING = Exchange("BASIC", "", "flask_server_meeting", "flask_server_meeting", MeetingResults.to_json, json.loads, False)
    FLASK_SERVER_SEQUENCE = Exchange("BASIC", "", "flask_server_sequence", "flask_server_sequence", SequenceResults.to_json, json.loads, False)
    CONNECTION_QUERY = Exchange("BASIC", "", "connection_query", "connection_query", json.dumps, ConnectionQuery.from_json, False)
    MEETING_QUERY = Exchange("BASIC", "", "meeting_query", "meeting_query", json.dumps, MeetingQuery.from_json, False)
    SEQUENCE_QUERY = Exchange("BASIC", "", "sequence_query", "sequence_query", json.dumps, SequenceQuery.from_json, False)
