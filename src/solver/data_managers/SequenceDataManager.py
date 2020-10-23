import pandas as pd
from src.solver.data_managers.DataManager import DataManager
from src.utils import load_pickle
from src.config import FloydDataPaths


class SequenceDataManager(DataManager):
    def get_data(self):
        data = dict()
        data["distances"] = load_pickle(FloydDataPaths.distances.value)
        data["stops_df"] = pd.read_pickle(FloydDataPaths.stops_df.value)
        data["stops_df_by_name"] = pd.read_pickle(FloydDataPaths.stops_df_by_name.value)
        return data

