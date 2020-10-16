import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from src.data_classes.Transfer import Transfer
from src.data_classes.WalkingTransfer import WalkingTransfer
from src.data_classes.ITransfer import ITransfer


@dataclass
class ConnectionResults:
    transfers: List[ITransfer]

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
    def to_json(connections):
        return json.dumps({"connections": [ConnectionResults.to_serializable(c) for c in connections]}, ensure_ascii=False)

    @staticmethod
    def from_json(json_file):
        json_dict = json.loads(json_file)
        return list(map(lambda c: ConnectionResults.from_serializable(c), json_dict))

    @staticmethod
    def to_serializable(connection):
        return {'transfers': [ConnectionResults.serialize_transfer(t) for t in connection.transfers]}

    @staticmethod
    def serialize_transfer(t):
        if type(t) is Transfer:
            return Transfer.to_serializable(t)
        return WalkingTransfer.to_serializable(t)

    @staticmethod
    def from_serializable(connection):
        connection_result = list(map(lambda t: t.from_serializable(t), connection))
        return ConnectionResults(connection_result)
