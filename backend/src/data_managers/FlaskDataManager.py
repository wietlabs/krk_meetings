import pandas as pd
from src.data_managers.DataManager import DataManager
from src.exchanges import EXCHANGES, MESSAGES
from src.config import FloydDataPaths


class FlaskDataManager(DataManager):
    @property
    def exchange(self):
        return EXCHANGES.FLASK_DATA_MANAGER.value

    def handle_message(self, msg):
        if msg == MESSAGES.DATA_UPDATED.value:
            self.update_data()

    def get_data(self):
        data = dict()
        stops_df: pd.DataFrame = pd.read_pickle(FloydDataPaths.stops_df.value)
        stops = [{"name": stop[1], "latitude": stop[2], "longitude": stop[3]} for stop in stops_df.itertuples()]
        data['stops'] = {'stops': stops}
        return data

