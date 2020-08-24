from dataclasses import dataclass
from datetime import date, time


@dataclass
class Transfer:
    route_number: str
    start_stop_name: str
    end_stop_name: str
    start_date: date
    start_time: time
    end_date: date
    end_time: time

    def __str__(self):
        return self.route_number + " " + self.start_stop_name + " " + str(self.start_date) + " " + str(self.start_time) \
               + " ==> " + self.end_stop_name + " " + str(self.end_date) + " " + str(self.end_time)
