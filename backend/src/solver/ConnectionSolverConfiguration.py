from dataclasses import dataclass


@dataclass
class ConnectionSolverConfiguration:
    max_searching_time: int
    partition_time: int
    max_travel_time: int
    number_of_connections_returned: int
    max_priority_multiplier: float
    max_priority_cap: int
    path_calculation_boost: float
    max_number_of_paths: int
    change_penalty: int
    max_path_calculation_time: int
    walking_route_id: int
    walking_index: tuple
