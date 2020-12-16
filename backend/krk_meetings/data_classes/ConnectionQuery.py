import json
from datetime import time, date, datetime
from dataclasses import dataclass
from krk_meetings.config import DATETIME_FORMAT
from krk_meetings.logger import get_logger

LOG = get_logger(__name__)

@dataclass
class ConnectionQuery:
    query_id: int
    start_datetime: datetime
    start_stop_name: str  # TODO: use class IPosition (Stop or Coordinates)?
    end_stop_name: str

    @staticmethod
    def from_json(connection):
        json_dict = json.loads(connection)
        return ConnectionQuery(
            json_dict["query_id"],
            datetime.strptime(json_dict["start_datetime"], DATETIME_FORMAT),
            json_dict["start_stop_name"],
            json_dict["end_stop_name"]
        )

    @staticmethod
    def from_dict(json_dict):
        return ConnectionQuery(
            0,
            datetime.strptime(json_dict["start_datetime"], DATETIME_FORMAT),
            json_dict["start_stop_name"],
            json_dict["end_stop_name"]
        )

    @staticmethod
    def validate(posted_json):
        try:
            query = ConnectionQuery.from_dict(posted_json)
            return True
        except (KeyError, ValueError):
            LOG.debug(f"Bad format of json for ConnectionQuery {posted_json}")
            return False
