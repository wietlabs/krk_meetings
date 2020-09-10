import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from src.data_classes.Transfer import Transfer


@dataclass
class ConnectionResults:
    transfers: List[Transfer]

    def __str__(self) -> str:
        return '\n'.join(map(str, self.transfers))

    def transfers_count(self) -> int:
        return len(self.transfers)

    def departure_time(self) -> datetime:
        return datetime.combine(self.transfers[0].start_date, self.transfers[0].start_time)

    def arrival_time(self) -> datetime:
        return datetime.combine(self.transfers[-1].end_date, self.transfers[-1].end_time)

    def duration(self, departure_time: datetime = None) -> timedelta:
        if departure_time is None:
            departure_time = self.departure_time()
        return self.arrival_time() - departure_time

    @staticmethod
    def to_json(connections):
        return json.dumps(list(map(lambda c: ConnectionResults.to_serializable(c), connections)), ensure_ascii=False)

    @staticmethod
    def from_json(json_file):
        json_dict = json.loads(json_file)
        return list(map(lambda c: ConnectionResults.from_serializable(c), json_dict))

    @staticmethod
    def to_serializable(connection):
        #print(connection)
        return list(map(lambda t: Transfer.to_serializable(t), connection.transfers))

    @staticmethod
    def from_serializable(connection):
        connection_result = list(map(lambda t: Transfer.from_serializable(t), connection))
        return ConnectionResults(connection_result)