import json
from dataclasses import dataclass


@dataclass
class SequenceResults:
    query_id: int
    error: dict
    best_sequence: list

    @staticmethod
    def to_json(sequence):
        return json.dumps({
            "query_id": sequence.query_id,
            "result": {"best_sequence": sequence.best_sequence},
            "error": sequence.error
        })
