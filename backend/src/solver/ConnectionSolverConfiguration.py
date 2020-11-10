from dataclasses import dataclass


@dataclass
class ConnectionSolverConfiguration:
    max_searching_time: int
    partition_time: int
    partition_search_range: int
    number_of_connections_returned: int
    max_priority_multiplier: float
    max_number_of_paths: int
    change_penalty: int
