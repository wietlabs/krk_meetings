from src.solver.data_managers.DataManager import DataManager
from src.utils import load_pickle
from src.config import FloydDataPaths


class MeetingDataManager(DataManager):
    def get_data(self):
        data = dict()
        data["distances"] = load_pickle(FloydDataPaths.distances.value)
        data["stops_df"] = load_pickle(FloydDataPaths.stops_df.value)
        data["stops_df_by_name"] = load_pickle(FloydDataPaths.stops_df_by_name.value)
        return data

