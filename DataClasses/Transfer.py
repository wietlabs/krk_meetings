from dataclasses import dataclass


@dataclass
class Transfer:
    # TODO: str or int - str better - it's processed to the client
    route_number: str
    start_stop_name: str
    end_stop_name: str
    start_time: str
    end_time: str
