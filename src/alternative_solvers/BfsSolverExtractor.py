from typing import Optional

import networkx as nx
import pandas as pd

from src.alternative_solvers.BfsSolverData import BfsSolverData
from src.data_classes.ParsedData import ParsedData


class BfsSolverExtractor:
    def __init__(self, boarding_edge_weight: Optional[int] = None):
        self.boarding_edge_weight = boarding_edge_weight

    def extract(self, parsed_data: ParsedData):
        calendar_df = parsed_data.calendar_df
        trips_df = parsed_data.trips_df
        transfers_df = parsed_data.transfers_df

        DAY = 24 * 60 * 60
        WEEK = 7 * DAY

        offsets = {
            service_id: [
                weekday * DAY
                for weekday, is_valid in enumerate(weekdays)
                if is_valid
            ]
            for service_id, *weekdays in calendar_df.itertuples()
        }

        transfers_min_df = transfers_df[['start_time', 'end_time', 'start_stop_id', 'end_stop_id', 'duration',
                                         'block_id', 'trip_num', 'service_id']]

        def gen():
            for service_id, group in transfers_min_df.groupby('service_id'):
                for offset in offsets[service_id]:
                    group = group.copy()
                    group[['start_time', 'end_time']] += offset
                    yield group

        # TODO: check offsets_df & join

        transfers_min_df = pd.concat(gen())
        transfers_min_df[['start_time', 'end_time']] %= WEEK

        unique_stop_times_df = transfers_min_df[['start_stop_id', 'start_time']].drop_duplicates()
        unique_stop_times_df.columns = ['stop_id', 'departure_time']
        unique_stop_times_df.set_index(['stop_id', 'departure_time'], inplace=True)
        unique_stop_times_df.sort_index(inplace=True)

        G = nx.DiGraph()

        G.add_weighted_edges_from(
            (
                (start_stop_id, start_time),
                (end_stop_id, end_time),
                duration
            )
            for start_time, end_time, start_stop_id, end_stop_id, duration, _, _, _ in transfers_min_df.itertuples(index=False)
        )

        G.add_weighted_edges_from(
            (
                (stop_id, start_time),
                (stop_id, end_time),
                (end_time - start_time) % WEEK
            )
            for stop_id, df in unique_stop_times_df.groupby('stop_id')
            for (_, start_time), (_, end_time) in nx.utils.pairwise(df.index, cyclic=True)
        )

        G_R = G.reverse()

        G.add_edges_from((
            (
                (stop_id, time),
                (stop_id, None)
            )
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        G_R.add_edges_from((
            (
                (stop_id, time),
                (stop_id, None)
            )
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        if self.boarding_edge_weight is not None:
            boarding_edge_weight = self.boarding_edge_weight
        else:
            max_duration = transfers_df.groupby(['service_id', 'block_id', 'trip_num'])['duration'].sum().max()
            boarding_edge_weight = max_duration

        G_T = nx.DiGraph()

        G_T.add_weighted_edges_from((
            (
                (start_stop_id, start_time, block_id, trip_num, service_id),
                (end_stop_id, end_time, block_id, trip_num, service_id),
                duration
            )
            for start_time, end_time, start_stop_id, end_stop_id, duration, block_id, trip_num, service_id in transfers_min_df.itertuples(index=False)
        ))

        G_T.add_edges_from((
            (
                (start_stop_id, start_time, None, None, None),
                (start_stop_id, start_time, block_id, trip_num, service_id)
            )
            for start_time, _, start_stop_id, _, _, block_id, trip_num, service_id in transfers_min_df.itertuples(index=False)
        ), weight=boarding_edge_weight)

        G_T.add_edges_from((
            (
                (end_stop_id, end_time, block_id, trip_num, service_id),
                (end_stop_id, end_time, None, None, None)
            )
            for _, end_time, _, end_stop_id, _, block_id, trip_num, service_id in transfers_min_df.itertuples(index=False)
        ), weight=0)

        G_T.add_weighted_edges_from((
            (
                (stop_id, start_time, None, None, None),
                (stop_id, end_time, None, None, None),
                (end_time - start_time) % WEEK
            )
            for stop_id, df in unique_stop_times_df.groupby('stop_id')
            for (_, start_time), (_, end_time) in nx.utils.pairwise(df.index, cyclic=True)
        ))

        G_T.add_edges_from((
            (
                (stop_id, time, None, None, None),
                (stop_id, None, None, None, None)
            )
            for stop_id, time in unique_stop_times_df.index
        ), weight=0)

        return BfsSolverData(G, G_R, G_T, unique_stop_times_df, trips_df)
