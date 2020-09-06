import json
from datetime import time, date, datetime
from dataclasses import dataclass


@dataclass
class ConnectionQuery:
    query_id: int
    start_date: date  # TODO: use datetime?
    start_time: time
    start_stop_name: str  # TODO: use class IPosition (Stop or Coordinates)?
    end_stop_name: str

    @staticmethod
    def to_json(connection):
        return json.dumps({
            "query_id": connection.query_id,
            "start_date": connection.start_date.strftime("%m/%d/%Y"),
            "start_time": connection.start_time.strftime("%H:%M:%S"),
            "start_stop_name": connection.start_stop_name,
            "end_stop_name": connection.end_stop_name
        })

    @staticmethod
    def from_json(connection):
        json_dict = json.loads(connection)
        return ConnectionQuery(
            json_dict["query_id"],
            datetime.strptime(json_dict["start_date"], "%d/%m/%Y").date(),
            datetime.strptime(json_dict["start_time"], "%H:%M:%S").time(),
            json_dict["start_stop_name"],
            json_dict["end_stop_name"]
        )
