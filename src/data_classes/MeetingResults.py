import json
from dataclasses import dataclass


@dataclass
class MeetingResults:
    query_id: int
    meeting_points: list

    @staticmethod
    def to_json(meeting):
        return json.dumps({
            "query_id": meeting.query_id,
            "result": {"meeting_points": meeting.meeting_points}
        })

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return MeetingResults(
            json_dict["query_id"],
            json_dict["meeting_points"]
        )
