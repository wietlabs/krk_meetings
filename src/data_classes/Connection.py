from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from src.data_classes.Transfer import Transfer


@dataclass
class Connection:
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
