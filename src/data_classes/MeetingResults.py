import json
from dataclasses import dataclass


@dataclass
class MeetingResults:
    meeting_points: list

    @staticmethod
    def to_json(meeting):
        return json.dumps({
            "meeting_points": meeting.meeting_points,
        })

    @staticmethod
    def from_json(meeting):
        json_dict = json.loads(meeting)
        return MeetingResults(
            json_dict["meeting_points"]
        )
