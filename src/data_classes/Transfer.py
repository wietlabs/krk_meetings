import json
from dataclasses import dataclass
from datetime import date, time, datetime
from src.config import DATETIME_FORMAT

@dataclass
class Transfer:
    route_id: int
    start_stop_id: int
    end_stop_id: int
    start_datetime: datetime
    end_datetime: datetime

    @staticmethod
    def to_serializable(transfer):
        return {
            "route_id": int(transfer.route_id),
            "start_stop_id": int(transfer.start_stop_id),
            "end_stop_id": int(transfer.end_stop_id),
            "start_datetime": transfer.start_datetime.strftime(DATETIME_FORMAT),
            "end_datetime": transfer.end_datetime.strftime(DATETIME_FORMAT),
        }

    @staticmethod
    def from_serializable(transfer):
        return Transfer(
            transfer["route_id"],
            transfer["start_stop_id"],
            transfer["end_stop_id"],
            datetime.strptime(transfer["start_date"], DATETIME_FORMAT),
            datetime.strptime(transfer["end_date"], DATETIME_FORMAT)
        )

    def __str__(self):
        return str(self.route_id) + " " + str(self.start_stop_id) + " " + str(self.start_datetime) \
               + " ==> " + str(self.end_stop_id) + " " + str(self.end_datetime)
