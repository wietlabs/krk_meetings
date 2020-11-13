import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from src.config import DATETIME_FORMAT
from src.data_classes.Transfer import Transfer
from src.data_classes.Walk import Walk
from src.data_classes.IAction import IAction


@dataclass
class Connection:
    walking_only: bool
    start_stop_name: str
    end_stop_name: str
    start_datetime: datetime
    end_datetime: datetime
    transfers: List[IAction]

    def __str__(self) -> str:
        return '\n'.join(map(str, self.transfers))

    def transfers_count(self) -> int:
        return len(self.transfers)

    def departure_time(self) -> datetime:
        return self.transfers[0].start_datetime

    def arrival_time(self) -> datetime:
        return self.transfers[-1].end_datetime

    def duration(self, departure_time: datetime = None) -> timedelta:
        if departure_time is None:
            departure_time = self.departure_time()
        return self.arrival_time() - departure_time

    @staticmethod
    def to_serializable(connection):
        return {
            "walking_only": connection.walking_only,
            "start_stop_name": connection.start_stop_name,
            "end_stop_name": connection.end_stop_name,
            "start_datetime": connection.start_datetime.strftime(DATETIME_FORMAT),
            "end_datetime": connection.end_datetime.strftime(DATETIME_FORMAT),
            'transfers': [Connection.serialize_transfer(t) for t in connection.transfers]
        }

    @staticmethod
    def serialize_transfer(t):
        if type(t) is Transfer:
            return Transfer.to_serializable(t)
        return Walk.to_serializable(t)
