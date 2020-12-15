import pandas as pd
from krk_meetings.data_managers.DataManager import DataManager
from krk_meetings.exchanges import EXCHANGES, MESSAGES
from krk_meetings.utils import load_pickle
from krk_meetings.config import FloydDataPaths


class MeetingDataManager(DataManager):
    def __init__(self, data_path):
        super().__init__()
        self.data_path = data_path

    @property
    def exchange(self):
        return EXCHANGES.MEETING_DATA_MANAGER.value

    def handle_message(self, msg):
        if msg == MESSAGES.DATA_UPDATED.value:
            self.update_data()

    def get_data(self):
        data = dict()
        data["distances"] = load_pickle(self.data_path.distances.value)
        data["stops_df"] = pd.read_pickle(self.data_path.stops_df.value)
        data["stops_df_by_name"] = pd.read_pickle(self.data_path.stops_df_by_name.value)
        return data

