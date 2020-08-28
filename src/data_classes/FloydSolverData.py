import json

import networkx as nx
import pandas as pd
from dataclasses import dataclass
from src.data_classes.Data import Data
from networkx.readwrite import json_graph


@dataclass
class FloydSolverData(Data):  # server has reference to its instance
    graph: nx.DiGraph
    kernelized_graph: nx.DiGraph
    distances_dict: dict
    day_to_services_dict: dict
    stop_times_0_dict: dict
    stop_times_24_dict: dict
    stops_df: pd.DataFrame
    routes_df: pd.DataFrame
    stops_df_by_name: pd.DataFrame

    @staticmethod
    def from_json(json_file):
        json_dict = json.loads(json_file)
        return FloydSolverData(
            nx.node_link_graph(json_dict["graph"]),
            nx.node_link_graph(json_dict["kernelized_graph"]),
            json_dict["distances_dict"],
            json_dict["day_to_services_dict"],
            FloydSolverData.map_nested_dict(FloydSolverData.df_from_json, json_dict["stop_times_0_dict"]),
            FloydSolverData.map_nested_dict(FloydSolverData.df_from_json, json_dict["stop_times_24_dict"]),
            pd.read_json(json_dict["stops_df"]),
            pd.read_json(json_dict["routes_df"]),
            pd.read_json(json_dict["stops_df_by_name"])
        )

    @staticmethod
    def to_json(data):
        return json.dumps({
            "graph": nx.node_link_data(data.graph),
            "kernelized_graph": nx.node_link_data(data.kernelized_graph),
            "distances_dict": data.distances_dict,
            "day_to_services_dict": data.day_to_services_dict,
            "stop_times_0_dict": data.map_nested_dict(data.df_to_json, data.stop_times_0_dict),
            "stop_times_24_dict": data.map_nested_dict(data.df_to_json, data.stop_times_24_dict),
            "stops_df": data.stops_df.to_json(),
            "routes_df": data.routes_df.to_json(),
            "stops_df_by_name": data.stops_df_by_name.to_json()
        })

    @staticmethod
    def map_nested_dict(function, nested_dict: dict) -> dict:
        for nested_key in nested_dict.keys():
            in_dict = nested_dict[nested_key]
            for key in in_dict.keys():
                in_dict[key] = function(in_dict[key])
        return nested_dict

    @staticmethod
    def df_to_json(df: pd.DataFrame) -> json:
        df = df.reset_index()
        return df.to_json()

    @staticmethod
    def df_from_json(df: json) -> pd.DataFrame:
        df = pd.read_json(df)
        df = df.set_index(['service_id', 'block_id', 'trip_num'])
        return df
