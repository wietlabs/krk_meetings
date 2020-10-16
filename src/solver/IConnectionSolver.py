from abc import ABC, abstractmethod

from src.data_classes.ConnectionResults import ConnectionResults
from src.data_classes.ConnectionQuery import ConnectionQuery
from typing import List


class IConnectionSolver(ABC):
    @abstractmethod
    def find_connections(self, query: ConnectionQuery) -> (int, List[ConnectionResults]):
        pass
