import json
from dataclasses import dataclass
from datetime import date, time, datetime
from src.config import DATETIME_FORMAT
from src.data_classes.IAction import IAction


@dataclass
class Transfer(IAction):
    route_name: str
    headsign: str
    start_stop_name: str
    end_stop_name: str
    start_datetime: datetime
    end_datetime: datetime
    stops: list

    def to_serializable(self):
        return {
            "type": "transfer",
            "route_name": self.route_name,
            "headsign": self.headsign,
            "start_stop_name": self.start_stop_name,
            "end_stop_name": self.end_stop_name,
            "start_datetime": self.start_datetime.strftime(DATETIME_FORMAT),
            "end_datetime": self.end_datetime.strftime(DATETIME_FORMAT),
            "stops": self.stops
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
        return f"{self.route_name} {self.headsign} {self.start_stop_name} {self.start_datetime} ==> {self.end_stop_name} {self.end_datetime}"
