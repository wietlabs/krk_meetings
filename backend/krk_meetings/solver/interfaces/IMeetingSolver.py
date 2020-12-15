from abc import ABC, abstractmethod
from krk_meetings.data_classes.MeetingQuery import MeetingQuery
from krk_meetings.data_classes.MeetingResults import MeetingResults


class IMeetingSolver(ABC):
    @abstractmethod
    def find_meeting_points(self, query: MeetingQuery) -> MeetingResults:
        pass
