from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from src.config import DATETIME_FORMAT
from src.data_classes.Transfer import Transfer
from src.data_classes.Walk import Walk
from src.data_classes.IAction import IAction


@dataclass
class Connection:
    actions: List[IAction]

    @property
    def transfers(self) -> List[Transfer]:
        return [action for action in self.actions if isinstance(action, Transfer)]

    @property
    def first_transfer(self) -> IAction:
        return self.transfers[0]

    @property
    def last_transfer(self) -> IAction:
        return self.transfers[-1]

    @property
    def starts_with_walk(self) -> bool:
        return isinstance(self.actions[0], Walk)

    @property
    def ends_with_walk(self) -> bool:
        return isinstance(self.actions[-1], Walk)

    @property
    def walk_only(self):
        return len(self.actions) == 1 and self.starts_with_walk

    @property
    def start_stop_name(self) -> Optional[str]:
        if self.walk_only:
            return None
        return self.first_transfer.start_stop_name

    @property
    def end_stop_name(self) -> Optional[str]:
        if self.walk_only:
            return None
        return self.last_transfer.end_stop_name

    @property
    def start_datetime(self) -> Optional[datetime]:
        if self.walk_only:
            return None
        return self.first_transfer.start_datetime

    @property
    def end_datetime(self) -> Optional[datetime]:
        if self.walk_only:
            return None
        return self.last_transfer.end_datetime

    def __str__(self) -> str:
        return '\n'.join(map(str, self.transfers))

    @property
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
        walk_only = connection.walk_only
        return {
            "walking_only": walk_only,
            "start_stop_name": None if walk_only else connection.start_stop_name,
            "end_stop_name": None if walk_only else connection.end_stop_name,
            "start_datetime": None if walk_only else connection.start_datetime.strftime(DATETIME_FORMAT),
            "end_datetime": None if walk_only else connection.end_datetime.strftime(DATETIME_FORMAT),
            "transfers_count": connection.transfers_count,
            "actions": [action.to_serializable() for action in connection.actions],
        }
