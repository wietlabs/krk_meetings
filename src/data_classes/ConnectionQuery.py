import json
from datetime import time, date, datetime
from dataclasses import dataclass


@dataclass
class ConnectionQuery:
    query_id: int
    start_date: date  # TODO: use datetime?
    start_time: time
    start_stop_id: int  # TODO: use class IPosition (Stop or Coordinates)?
    end_stop_id: int

    @staticmethod
    def to_json(connection):
        return json.dumps({
            "query_id": connection.query_id,
            "start_date": connection.start_date.strftime("%Y-%m-%d"),
            "start_time": connection.start_time.strftime("%H:%M:%S"),
            "start_stop_id": connection.start_stop_name,
            "end_stop_id": connection.end_stop_name
        })

    @staticmethod
    def from_json(connection):
        json_dict = json.loads(connection)
        return ConnectionQuery(
            json_dict["query_id"],
            datetime.strptime(json_dict["start_date"], "%Y-%m-%d").date(),
            datetime.strptime(json_dict["start_time"], "%H:%M:%S").time(),
            json_dict["start_stop_id"],
            json_dict["end_stop_id"]
        )
