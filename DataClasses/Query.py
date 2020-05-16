from dataclasses import dataclass


@dataclass
class Query:
    start_time: int  # TODO: use datetime?
    start_stop_id: int  # TODO: use class IPosition (Stop or Coordinates)?
    end_stop_id: int
