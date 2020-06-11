from dataclasses import dataclass

import pandas as pd
import networkx as nx

from DataClasses.Data import Data
from DataClasses.ExtractedData import ExtractedData
from DataClasses.ParsedData import ParsedData


@dataclass
class BfsSolverData(Data):
    G: nx.DiGraph
    G_R: nx.DiGraph
    stops_df: pd.DataFrame
    stops_df_by_name: pd.DataFrame
    unique_stop_times_df: pd.DataFrame

    @classmethod
    def create(cls, parsed_data: ParsedData, extracted_data: ExtractedData):
        stops_df = parsed_data.stops_df
        stops_df_by_name = extracted_data.stops_df_by_name
        stop_times_df = parsed_data.stop_times_df
        transfers_df = parsed_data.transfers_df

        transfers_df = transfers_df[['start_time', 'end_time', 'start_stop_id', 'end_stop_id', 'duration']]

        unique_stop_times_df = stop_times_df.reset_index()[['stop_id', 'departure_time']]
        unique_stop_times_df['departure_time'] %= 24 * 60 * 60
        unique_stop_times_df.drop_duplicates(inplace=True)
        unique_stop_times_df.set_index(['stop_id', 'departure_time'], inplace=True)
        unique_stop_times_df.sort_index(inplace=True)

        G = nx.DiGraph()

        G.add_nodes_from(unique_stop_times_df.index)

        G.add_weighted_edges_from(
            ((start_stop_id, start_time), (end_stop_id, end_time), duration)
            for _, start_time, end_time, start_stop_id, end_stop_id, duration in transfers_df.itertuples()
        )
        # TODO: include weekdays using service_id

        # trick #1: add destination nodes
        G.add_nodes_from(
            (stop_id, None)
            for stop_id in stops_df.index
        )

        # trick #2: merged waiting edges
        G.add_weighted_edges_from(
            ((stop_id, start_time), (stop_id, end_time), (end_time - start_time) % (24 * 60 * 60))
            for stop_id, df in unique_stop_times_df.groupby('stop_id')
            for (_, start_time), (_, end_time) in nx.utils.pairwise(df.index, cyclic=True)
        )

        # trick #3: use reversed graph to find the latest departure time
        G_R = G.reverse()

        G.add_edges_from((
            ((stop_id, time), (stop_id, None))
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        G_R.add_edges_from((
            ((stop_id, time), (stop_id, None))
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        return cls(G, G_R, stops_df, stops_df_by_name, unique_stop_times_df)
