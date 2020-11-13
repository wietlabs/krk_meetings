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
    transfers: List[IAction]

    @property
    def starts_with_walk(self) -> bool:
        return isinstance(self.transfers[0], Walk)

    @property
    def ends_with_walk(self) -> bool:
        return isinstance(self.transfers[-1], Walk)

    @property
    def walk_only(self):
        return len(self.transfers) == 1 and self.starts_with_walk

    @property
    def start_stop_name(self):
        if self.walk_only:
            return None
        if self.starts_with_walk:
            return self.transfers[1].start_stop_name
        return self.transfers[0].start_stop_name

    @property
    def end_stop_name(self):
        if self.walk_only:
            return None
        if self.starts_with_walk:
            return self.transfers[-2].end_stop_name
        return self.transfers[-1].end_stop_name

    @property
    def start_datetime(self):
        if self.walk_only:
            return None
        if self.starts_with_walk:
            return self.transfers[1].start_datetime
        return self.transfers[0].start_datetime

    @property
    def end_datetime(self):
        if self.walk_only:
            return None
        if self.ends_with_walk:
            return self.transfers[-2].end_datetime
        return self.transfers[-1].end_datetime

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
            "walking_only": connection.walk_only,
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
