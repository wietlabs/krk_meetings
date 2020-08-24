from dataclasses import dataclass


@dataclass
class MeetingQuery:
    start_stop_names: list  # TODO: use class IPosition (Stop or Coordinates)?
    metric: str
