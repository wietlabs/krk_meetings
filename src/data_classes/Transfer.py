import json
from dataclasses import dataclass
from datetime import date, time, datetime
from src.config import DATETIME_FORMAT
from src.data_classes.ITransfer import ITransfer


@dataclass
class Transfer(ITransfer):
    route_name: str
    headsign: str
    start_stop_name: str
    end_stop_name: str
    start_datetime: datetime
    end_datetime: datetime
    stops: list

    @staticmethod
    def to_serializable(transfer):
        return {
            "type": "transfer",
            "route_name": transfer.route_name,
            "headsign": transfer.headsign,
            "start_stop_name": transfer.start_stop_name,
            "end_stop_name": transfer.end_stop_name,
            "start_datetime": transfer.start_datetime.strftime(DATETIME_FORMAT),
            "end_datetime": transfer.end_datetime.strftime(DATETIME_FORMAT),
            "stops": transfer.stops
        }

    @staticmethod
    def from_serializable(transfer):
        return Transfer(
            transfer["route_name"],
            transfer["headsign"],
            transfer["start_stop_name"],
            transfer["end_stop_name"],
            datetime.strptime(transfer["start_date"], DATETIME_FORMAT),
            datetime.strptime(transfer["end_date"], DATETIME_FORMAT),
            transfer["stops"]
        )

    def __str__(self):
        return f"{self.route_id} {self.start_stop_name} {self.start_datetime} ==> {self.end_stop_name} {self.end_datetime}"
