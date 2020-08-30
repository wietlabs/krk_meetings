import json
from dataclasses import dataclass


@dataclass
class SequenceResults:
    best_sequence: list

    @staticmethod
    def to_json(meeting):
        return json.dumps({
            "best_sequence": meeting.best_sequence,
        })

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return SequenceResults(
            json_dict["best_sequence"]
        )
