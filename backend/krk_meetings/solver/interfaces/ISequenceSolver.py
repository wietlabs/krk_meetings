from abc import ABC, abstractmethod
from krk_meetings.data_classes.SequenceQuery import SequenceQuery
from krk_meetings.data_classes.SequenceResults import SequenceResults


class ISequenceSolver(ABC):
    @abstractmethod
    def find_best_sequence(self, query: SequenceQuery) -> SequenceResults:
        pass
