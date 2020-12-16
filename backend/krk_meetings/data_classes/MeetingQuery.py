import json
from dataclasses import dataclass
from krk_meetings.logger import get_logger

LOG = get_logger(__name__)

@dataclass
class MeetingQuery:
    query_id: int
    start_stop_names: list  # TODO: use class IPosition (Stop or Coordinates)?
    norm: str

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return MeetingQuery(
            json_dict["query_id"],
            json_dict["start_stop_names"],
            json_dict["norm"]
        )

    @staticmethod
    def from_dict(json_dict):
        return MeetingQuery(
            0,
            json_dict["start_stop_names"],
            json_dict["norm"]
        )

    @staticmethod
    def validate(posted_json):
        try:
            query = MeetingQuery.from_dict(posted_json)
            if len(query.start_stop_names) > 100:
                LOG.debug(f"To many start_stop_names. Amount of stops must be 100 or less.")
                return False
            return True
        except (KeyError, ValueError):
            LOG.debug(f"Bad format of json for MeetingQuery {posted_json}")
            return False


