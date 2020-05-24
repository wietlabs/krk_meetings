from datetime import time, date
from dataclasses import dataclass


@dataclass
class TransferQuery:
    start_date: date  # TODO: use datetime?
    start_time: time
    start_stop: str  # TODO: use class IPosition (Stop or Coordinates)?
    end_stop: str
