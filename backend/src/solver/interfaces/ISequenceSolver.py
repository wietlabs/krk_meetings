from abc import ABC, abstractmethod
from src.data_classes.SequenceQuery import SequenceQuery
from src.data_classes.SequenceResults import SequenceResults


class ISequenceSolver(ABC):
    @abstractmethod
    def find_best_sequence(self, query: SequenceQuery) -> SequenceResults:
        pass
