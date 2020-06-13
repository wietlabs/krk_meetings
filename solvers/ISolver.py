from abc import ABC, abstractmethod

from DataClasses.Connection import Connection
from DataClasses.TransferQuery import TransferQuery
from typing import List


class ISolver(ABC):
    @abstractmethod
    def find_connections(self, query: TransferQuery) -> List[Connection]:
        pass
