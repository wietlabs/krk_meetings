import json
from datetime import time, date, datetime
from dataclasses import dataclass
from src.config import DATETIME_FORMAT

@dataclass
class ConnectionQuery:
    query_id: int
    start_datetime: datetime
    start_stop_name: str  # TODO: use class IPosition (Stop or Coordinates)?
    end_stop_name: str

    @staticmethod
    def to_json(connection):
        return json.dumps({
            "query_id": connection.query_id,
            "start_datetime": connection.start_datetime.strftime(DATETIME_FORMAT),
            "start_stop_id": connection.start_stop_name,
            "end_stop_id": connection.end_stop_name
        })

    @staticmethod
    def from_json(connection):
        json_dict = json.loads(connection)
        return ConnectionQuery(
            json_dict["query_id"],
            datetime.strptime(json_dict["start_datetime"], DATETIME_FORMAT),
            json_dict["start_stop_name"],
            json_dict["end_stop_name"]
        )