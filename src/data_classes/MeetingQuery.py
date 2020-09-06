import json
from dataclasses import dataclass


@dataclass
class MeetingQuery:
    start_stop_names: list  # TODO: use class IPosition (Stop or Coordinates)?
    metric: str

    @staticmethod
    def to_json(meeting):
        return json.dumps({
            "start_stop_names": meeting.start_stop_names,
            "metric": meeting.metric
        })

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return MeetingQuery(
            json_dict["start_stop_names"],
            json_dict["metric"]
        )
