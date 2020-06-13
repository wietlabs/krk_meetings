from dataclasses import dataclass


@dataclass
class SequenceQuery:
    start_stop_name: str
    end_stop_name: str
    stops_to_visit: list  # TODO: use class IPosition (Stop or Coordinates)?
