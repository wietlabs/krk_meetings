from abc import ABC, abstractmethod
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.MeetingResults import MeetingResults


class IMeetingSolver(ABC):
    @abstractmethod
    def find_meeting_points(self, query: MeetingQuery) -> MeetingResults:
        pass
