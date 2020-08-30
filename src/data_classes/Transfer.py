import json
from dataclasses import dataclass
from datetime import date, time, datetime


@dataclass
class Transfer:
    route_number: str
    start_stop_name: str
    end_stop_name: str
    start_date: date
    start_time: time
    end_date: date
    end_time: time

    @staticmethod
    def to_serializable(transfer):
        return {
            "route_number": transfer.route_number,
            "start_stop_name": transfer.start_stop_name,
            "end_stop_name": transfer.end_stop_name,
            "start_date": transfer.start_date.strftime("%m/%d/%Y"),
            "start_time": transfer.start_time.strftime("%H:%M:%S"),
            "end_date": transfer.end_date.strftime("%m/%d/%Y"),
            "end_time": transfer.end_time.strftime("%H:%M:%S")
        }

    @staticmethod
    def from_serializable(transfer):
        return Transfer(
            transfer["route_number"],
            transfer["start_stop_name"],
            transfer["end_stop_name"],
            datetime.strptime(transfer["start_date"], "%m/%d/%Y").date(),
            datetime.strptime(transfer["start_time"], "%H:%M:%S").time(),
            datetime.strptime(transfer["end_date"], "%m/%d/%Y").date(),
            datetime.strptime(transfer["end_time"], "%H:%M:%S").time()
        )

    def __str__(self):
        return self.route_number + " " + self.start_stop_name + " " + str(self.start_date) + " " + str(self.start_time) \
               + " ==> " + self.end_stop_name + " " + str(self.end_date) + " " + str(self.end_time)
