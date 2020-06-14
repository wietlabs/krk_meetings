from typing import Optional

import networkx as nx

from DataClasses.ExtractedData import ExtractedData
from DataClasses.ParsedData import ParsedData
from solvers.BfsSolver.BfsSolverData import BfsSolverData


class BfsSolverExtractor:
    def __init__(self, boarding_edge_weight: Optional[int] = None):
        self.boarding_edge_weight = boarding_edge_weight

    def extract(self, parsed_data: ParsedData, extracted_data: ExtractedData):
        stops_df = parsed_data.stops_df
        stops_df_by_name = extracted_data.stops_df_by_name
        stop_times_df = parsed_data.stop_times_df
        transfers_df = parsed_data.transfers_df
        trips_df = parsed_data.trips_df
        routes_df = parsed_data.routes_df

        stop_times_min_df = stop_times_df.reset_index()[['stop_id', 'departure_time', 'block_id', 'trip_num', 'service_id']]
        transfers_min_df = transfers_df[['start_time', 'end_time', 'start_stop_id', 'end_stop_id', 'duration', 'block_id', 'trip_num', 'service_id']]

        unique_stop_times_df = stop_times_df.reset_index()[['stop_id', 'departure_time']]
        unique_stop_times_df['departure_time'] %= 24 * 60 * 60
        unique_stop_times_df.drop_duplicates(inplace=True)
        unique_stop_times_df.set_index(['stop_id', 'departure_time'], inplace=True)
        unique_stop_times_df.sort_index(inplace=True)

        G = nx.DiGraph()

        # G.add_nodes_from(unique_stop_times_df.index)

        G.add_weighted_edges_from(
            ((start_stop_id, start_time), (end_stop_id, end_time), duration)
            for _, start_time, end_time, start_stop_id, end_stop_id, duration, _, _, _ in transfers_min_df.itertuples()
        )

        # G.add_nodes_from(
        #     (stop_id, None)
        #     for stop_id in stops_df.index
        # )

        G.add_weighted_edges_from(
            ((stop_id, start_time), (stop_id, end_time), (end_time - start_time) % (24 * 60 * 60))
            for stop_id, df in unique_stop_times_df.groupby('stop_id')
            for (_, start_time), (_, end_time) in nx.utils.pairwise(df.index, cyclic=True)
        )

        G_R = G.reverse()

        G.add_edges_from((
            ((stop_id, time), (stop_id, None))
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        G_R.add_edges_from((
            ((stop_id, time), (stop_id, None))
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        if self.boarding_edge_weight is not None:
            boarding_edge_weight = self.boarding_edge_weight
        else:
            boarding_edge_weight = transfers_df.groupby(['service_id', 'block_id', 'trip_num'])['duration'].sum().max()

        G_T = nx.DiGraph()

        G_T.add_weighted_edges_from((
            ((start_stop_id, start_time, block_id, trip_num, service_id), (end_stop_id, end_time, block_id, trip_num, service_id), duration)
            for _, start_time, end_time, start_stop_id, end_stop_id, duration, block_id, trip_num, service_id in transfers_min_df.itertuples()
        ))

        G_T.add_edges_from((
            ((stop_id, time, None, None, None), (stop_id, time, block_id, trip_num, service_id))
            for _, stop_id, time, block_id, trip_num, service_id in stop_times_min_df.itertuples()
        ), weight=boarding_edge_weight)

        G_T.add_edges_from((
            ((stop_id, time, block_id, trip_num, service_id), (stop_id, time, None, None, None))
            for _, stop_id, time, block_id, trip_num, service_id in stop_times_min_df.itertuples()
        ), weight=0)

        G_T.add_weighted_edges_from((
            ((stop_id, start_time, None, None, None), (stop_id, end_time, None, None, None), (end_time - start_time) % (24 * 60 * 60))
            for stop_id, df in unique_stop_times_df.groupby('stop_id')
            for (_, start_time), (_, end_time) in nx.utils.pairwise(df.index, cyclic=True)
        ))

        G_T.add_edges_from((
            ((stop_id, time, None, None, None), (stop_id, None, None, None, None))
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        return BfsSolverData(G, G_R, G_T, stops_df, stops_df_by_name, unique_stop_times_df, trips_df, routes_df)
