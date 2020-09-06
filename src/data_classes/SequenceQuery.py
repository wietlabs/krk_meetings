import json
from dataclasses import dataclass


@dataclass
class SequenceQuery:
    start_stop_name: str
    end_stop_name: str
    stops_to_visit: list  # TODO: use class IPosition (Stop or Coordinates)?

    @staticmethod
    def to_json(meeting):
        return json.dumps({
            "start_stop_name": meeting.start_stop_name,
            "end_stop_name": meeting.end_stop_name,
            "stops_to_visit": meeting.stops_to_visit
        })

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return SequenceQuery(
            json_dict["start_stop_name"],
            json_dict["end_stop_name"],
            json_dict["stops_to_visit"]
        )
