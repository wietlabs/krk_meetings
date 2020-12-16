import json
from dataclasses import dataclass
from krk_meetings.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SequenceQuery:
    query_id: int
    start_stop_name: str
    end_stop_name: str
    stops_to_visit: list  # TODO: use class IPosition (Stop or Coordinates)?

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return SequenceQuery(
            json_dict["query_id"],
            json_dict["start_stop_name"],
            json_dict["end_stop_name"],
            json_dict["stops_to_visit"]
        )

    @staticmethod
    def from_dict(json_dict):
        return SequenceQuery(
            0,
            json_dict["start_stop_name"],
            json_dict["end_stop_name"],
            json_dict["stops_to_visit"]
        )

    @staticmethod
    def validate(posted_json):
        try:
            query = SequenceQuery.from_dict(posted_json)
            if len(query.stops_to_visit) > 8:
                logger.debug(f"To many stops_to_visit. Amount of stops must be 8 or less.")
                return False
            return True
        except (KeyError, ValueError):
            logger.debug(f"Bad format of json for MeetingQuery {posted_json}")
            return False
