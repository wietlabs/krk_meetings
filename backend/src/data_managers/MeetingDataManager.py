import pandas as pd
from src.data_managers.DataManager import DataManager
from src.exchanges import EXCHANGES, MESSAGES
from src.utils import load_pickle
from src.config import FloydDataPaths


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
        data["distances"] = load_pickle(FloydDataPaths.distances.value)
        data["stops_df"] = pd.read_pickle(FloydDataPaths.stops_df.value)
        data["stops_df_by_name"] = pd.read_pickle(FloydDataPaths.stops_df_by_name.value)
        return data

