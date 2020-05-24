from abc import ABC, abstractmethod
from DataClasses.TransferQuery import Query
from typing import List


class ISolver(ABC):
    @abstractmethod
    def find_connection(self, query: Query) -> List[List[object]]:
        pass
