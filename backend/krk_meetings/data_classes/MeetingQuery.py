import json
from dataclasses import dataclass


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
                return False
            return True
        except (KeyError, ValueError):
            return False


