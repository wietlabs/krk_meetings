import json
from dataclasses import dataclass
from datetime import datetime
from krk_meetings.data_classes.IAction import IAction


@dataclass
class Walk(IAction):
    start_stop_name: int
    end_stop_name: int
    duration_in_minutes: int
    start_datetime: datetime
    end_datetime: datetime
    stops: list

    def to_serializable(self):
        return {
            "type": "walking",
            "start_stop_name": self.start_stop_name,
            "end_stop_name": self.end_stop_name,
            "duration_in_minutes": int(self.duration_in_minutes),
            "stops": self.stops
        }

    @classmethod
    def from_serializable(cls, walk):
        return cls(
            walk["start_stop_name"],
            walk["end_stop_name"],
            walk["duration_in_minutes"],
            walk["start_datetime"],
            walk["end_datetime"],
            walk["stops"]
        )

    def __str__(self):
        return f"{self.start_stop_name} ==> {self.end_stop_name} {self.duration_in_minutes}"
