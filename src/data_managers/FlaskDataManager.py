import pandas as pd
from src.data_managers.DataManager import DataManager
from src.utils import load_pickle
from src.config import FloydDataPaths


class FlaskDataManager(DataManager):
    def get_data(self):
        data = dict()
        stops_df: pd.DataFrame = pd.read_pickle(FloydDataPaths.stops_df.value)
        stops = [{"name": stop[1], "latitude": stop[2], "longitude": stop[3]} for stop in stops_df.itertuples()]
        data['stops'] = {'stops': stops}
        return data


if __name__ =="__main__":
    data_manager = FlaskDataManager()
    data_manager.get_data()
