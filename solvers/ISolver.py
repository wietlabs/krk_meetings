from abc import ABC, abstractmethod
from solvers.Query import Query


class ISolver(ABC):
    @abstractmethod
    def find_connection(self, query: Query):
        pass
