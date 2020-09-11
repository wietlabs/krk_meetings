import json
from dataclasses import dataclass
from datetime import date, time, datetime


@dataclass
class Transfer:
    route_id: int
    start_stop_id: int
    end_stop_id: int
    start_date: date
    start_time: time
    end_date: date
    end_time: time

    @staticmethod
    def to_serializable(transfer):
        return {
            "route_id": int(transfer.route_id),
            "start_stop_id": int(transfer.start_stop_id),
            "end_stop_id": int(transfer.end_stop_id),
            "start_date": transfer.start_date.strftime("%Y-%m-%d"),
            "start_time": transfer.start_time.strftime("%H:%M:%S"),
            "end_date": transfer.end_date.strftime("%Y-%m-%d"),
            "end_time": transfer.end_time.strftime("%H:%M:%S")
        }

    @staticmethod
    def from_serializable(transfer):
        return Transfer(
            transfer["route_id"],
            transfer["start_stop_id"],
            transfer["end_stop_id"],
            datetime.strptime(transfer["start_date"], "%Y-%m-%d").date(),
            datetime.strptime(transfer["start_time"], "%H:%M:%S").time(),
            datetime.strptime(transfer["end_date"], "%Y-%m-%d").date(),
            datetime.strptime(transfer["end_time"], "%H:%M:%S").time()
        )

    def __str__(self):
        return str(self.route_id) + " " + str(self.start_stop_id) + " " + str(self.start_date) + " " + str(self.start_time) \
               + " ==> " + str(self.end_stop_id) + " " + str(self.end_date) + " " + str(self.end_time)
