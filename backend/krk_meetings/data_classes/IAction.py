from datetime import datetime


class IAction:
    start_stop_name: str
    end_stop_name: str
    start_datetime: datetime
    end_datetime: datetime

    def __str__(self):
        return f"{self.start_stop_name} {self.start_datetime} ==> {self.end_stop_name} {self.end_datetime}"
