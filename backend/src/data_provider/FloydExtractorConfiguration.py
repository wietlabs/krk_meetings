from dataclasses import dataclass


@dataclass
class FloydExtractorConfiguration:
    daily_period_multiplier: float
    nightly_period_multiplier: float
    change_penalty: int
    nightly_route_ranges: list
    daily_hours: int
    nightly_hours: int
    walking_route_id: int
    number_of_services: int


