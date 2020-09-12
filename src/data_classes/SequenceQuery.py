import json
from dataclasses import dataclass


@dataclass
class SequenceQuery:
    query_id: int
    start_stop_name: str
    end_stop_name: str
    stops_to_visit: list  # TODO: use class IPosition (Stop or Coordinates)?

    @staticmethod
    def to_json(sequence):
        return json.dumps({
            "query_id": sequence.query_id,
            "start_stop_name": sequence.start_stop_name,
            "end_stop_name": sequence.end_stop_name,
            "stops_to_visit": sequence.stops_to_visit
        })

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return SequenceQuery(
            json_dict["query_id"],
            json_dict["start_stop_name"],
            json_dict["end_stop_name"],
            json_dict["stops_to_visit"]
        )
