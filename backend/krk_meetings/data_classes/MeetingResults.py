import json
from dataclasses import dataclass


@dataclass
class MeetingResults:
    query_id: int
    error: dict
    meeting_points: list

    @staticmethod
    def to_json(meeting):
        return json.dumps({
            "query_id": meeting.query_id,
            "result": {"meeting_points": meeting.meeting_points},
            "error": meeting.error
        })
