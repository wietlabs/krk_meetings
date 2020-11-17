import json
from dataclasses import dataclass


@dataclass
class MeetingQuery:
    query_id: int
    start_stop_names: list  # TODO: use class IPosition (Stop or Coordinates)?
    metric: str

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return MeetingQuery(
            json_dict["query_id"],
            json_dict["start_stop_names"],
            json_dict["metric"]
        )

    @staticmethod
    def from_dict(json_dict):
        return MeetingQuery(
            0,
            json_dict["start_stop_names"],
            json_dict["metric"]
        )
