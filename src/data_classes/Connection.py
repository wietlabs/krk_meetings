import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from src.data_classes.Transfer import Transfer
from src.data_classes.Walk import Walk
from src.data_classes.IAction import IAction


@dataclass
class Connection:
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
        return {'transfers': [Connection.serialize_transfer(t) for t in connection.transfers]}

    @staticmethod
    def serialize_transfer(t):
        if type(t) is Transfer:
            return Transfer.to_serializable(t)
        return Walk.to_serializable(t)
