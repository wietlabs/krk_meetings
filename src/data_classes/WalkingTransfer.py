import json
from dataclasses import dataclass
from datetime import datetime
from src.data_classes.ITransfer import ITransfer


@dataclass
class WalkingTransfer(ITransfer):
    start_stop_name: int
    end_stop_name: int
    duration_in_minutes: int
    start_datetime: datetime
    end_datetime: datetime

    @staticmethod
    def to_serializable(walking_transfer):
        return {
            "type": "walking",
            "start_stop_name": walking_transfer.start_stop_name,
            "end_stop_name": walking_transfer.end_stop_name,
            "duration_in_minutes": int(walking_transfer.duration_in_minutes)
        }

    @staticmethod
    def from_serializable(walking_transfer):
        return WalkingTransfer(
            walking_transfer["start_stop_name"],
            walking_transfer["end_stop_name"],
            walking_transfer["duration_in_minutes"],
            walking_transfer["start_datetime"],
            walking_transfer["end_datetime"]
        )

    def __str__(self):
        return str(self.start_stop_name) + " ==> " + str(self.end_stop_name) + " " + str(self.duration_in_minutes)
