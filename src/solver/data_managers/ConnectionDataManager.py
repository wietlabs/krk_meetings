from src.solver.data_managers.DataManager import DataManager
from src.utils import load_pickle
from src.config import FloydDataPaths


class ConnectionDataManager(DataManager):
    def get_data(self):
        data = dict()
        data["graph"] = load_pickle(FloydDataPaths.floyd_graph.value)
        data["kernelized_graph"] = load_pickle(FloydDataPaths.kernelized_floyd_graph.value)
        data["distances"] = load_pickle(FloydDataPaths.distances.value)
        data["stops_df"] = load_pickle(FloydDataPaths.stops_df.value)
        data["routes_df"] = load_pickle(FloydDataPaths.routes_df.value)
        data["stops_df_by_name"] = load_pickle(FloydDataPaths.stops_df_by_name.value)
        data["stop_times_0"] = load_pickle(FloydDataPaths.stop_times_0_dict.value)
        data["stop_times_24"] = load_pickle(FloydDataPaths.stop_times_0_dict.value)
        data["day_to_services_dict"] = load_pickle(FloydDataPaths.day_to_services_dict.value)
        data["adjacent_stops"] = load_pickle(FloydDataPaths.adjacent_stops.value)
        data["routes_to_stops_dict"] = load_pickle(FloydDataPaths.routes_to_stops_dict.value)
        return data
