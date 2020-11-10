import json
from dataclasses import dataclass


@dataclass
class SequenceResults:
    query_id: int
    best_sequence: list

    @staticmethod
    def to_json(meeting):
        return json.dumps({
            "query_id": meeting.query_id,
            "result": {"best_sequence": meeting.best_sequence}
        })

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return SequenceResults(
            json_dict["query_id"],
            json_dict["best_sequence"]
        )
