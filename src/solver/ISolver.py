from abc import ABC, abstractmethod

from src.data_classes.Connection import Connection
from src.data_classes.TransferQuery import TransferQuery
from typing import List


class ISolver(ABC):
    @abstractmethod
    def find_connections(self, query: TransferQuery) -> List[Connection]:
        pass
