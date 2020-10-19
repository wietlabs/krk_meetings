from copy import deepcopy
from typing import Tuple

import pandas as pd

from src.data_classes.ParsedData import ParsedData


class Merger:
    def merge(self, parsed_data_1: ParsedData, parsed_data_2: ParsedData) -> ParsedData:
        parsed_data_2 = deepcopy(parsed_data_2)

        calendar_df, service_id_offset = self._merge_calendar_dfs(parsed_data_1.calendar_df,
                                                                  parsed_data_2.calendar_df)

        calendar_dates_df = self._merge_calendar_dates_dfs(parsed_data_1.calendar_dates_df,
                                                           parsed_data_2.calendar_dates_df,
                                                           service_id_offset)

        routes_df, route_id_offset = self._merge_routes_df(parsed_data_1.routes_df,
                                                           parsed_data_2.routes_df)

        trips_df = self._merge_trips_df(parsed_data_1.trips_df,
                                        parsed_data_2.trips_df,
                                        service_id_offset, route_id_offset)

        stops_df, stop_id_offset, stop_id_mapping = self._merge_stops_df(parsed_data_1.stops_df,
                                                                         parsed_data_2.stops_df)

        perons_df, peron_id_offset = self._merge_perons_df(parsed_data_1.perons_df,
                                                           parsed_data_2.perons_df,
                                                           stop_id_offset, stop_id_mapping)

        stop_times_df = self._merge_stop_times_df(parsed_data_1.stop_times_df,
                                                  parsed_data_2.stop_times_df,
                                                  service_id_offset, stop_id_offset, stop_id_mapping, peron_id_offset)

        transfers_df = self._merge_transfers_df(parsed_data_1.transfers_df,
                                                parsed_data_2.transfers_df,
                                                service_id_offset, stop_id_offset, stop_id_mapping, peron_id_offset)

        return ParsedData(calendar_df=calendar_df,
                          calendar_dates_df=calendar_dates_df,
                          routes_df=routes_df,
                          trips_df=trips_df,
                          stops_df=stops_df,
                          perons_df=perons_df,
                          stop_times_df=stop_times_df,
                          transfers_df=transfers_df)

    def _merge_calendar_dfs(self, calendar_df_1: pd.DataFrame, calendar_df_2: pd.DataFrame) -> Tuple[
        pd.DataFrame, int]:
        service_id_offset = calendar_df_1.index.max()

        calendar_df_2.reset_index(inplace=True)
        calendar_df_2.loc[:, 'service_id'] += service_id_offset
        calendar_df_2.set_index('service_id', inplace=True)

        calendar_df = calendar_df_1.append(calendar_df_2)
        return calendar_df, service_id_offset

    def _merge_calendar_dates_dfs(self, calendar_dates_df_1: pd.DataFrame, calendar_dates_df_2: pd.DataFrame,
                                  service_id_offset: int) -> Tuple[pd.DataFrame, int]:
        calendar_dates_df_2.loc[:, 'service_id'] += service_id_offset

        calendar_dates_df = calendar_dates_df_1.append(calendar_dates_df_2)
        calendar_dates_df.reset_index(drop=True, inplace=True)
        calendar_dates_df.sort_values(by=['date', 'exception_type', 'service_id'], inplace=True)
        return calendar_dates_df

    def _merge_routes_df(self, routes_df_1: pd.DataFrame, routes_df_2: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        route_id_offset = routes_df_1.index.max()

        routes_df_2.reset_index(inplace=True)
        routes_df_2.loc[:, 'route_id'] += route_id_offset
        routes_df_2.set_index('route_id', inplace=True)

        routes_df = routes_df_1.append(routes_df_2)
        return routes_df, route_id_offset

    def _merge_trips_df(self, trips_df_1: pd.DataFrame, trips_df_2: pd.DataFrame,
                        service_id_offset: int, route_id_offset: int) -> pd.DataFrame:
        trips_df_2.reset_index(inplace=True)
        trips_df_2.loc[:, 'service_id'] += service_id_offset
        trips_df_2.loc[:, 'route_id'] += route_id_offset
        trips_df_2.set_index(['service_id', 'block_id', 'trip_num'], inplace=True)

        trips_df = trips_df_1.append(trips_df_2)
        return trips_df

    def _merge_stops_df(self, stops_df_1: pd.DataFrame, stops_df_2: pd.DataFrame) -> Tuple[
        pd.DataFrame, int, pd.Series]:
        stop_id_offset = stops_df_1.index.max()

        stops_df_2.reset_index(inplace=True)
        stops_df_2.loc[:, 'stop_id'] += stop_id_offset
        stops_df_2.set_index('stop_id', inplace=True)

        stops_df = stops_df_1.append(stops_df_2)

        stops_df.reset_index(inplace=True)
        stops_df.set_index('stop_name', inplace=True)
        stops_df = stops_df.groupby('stop_name').agg({
            'stop_id': ['min', 'max'],
            'stop_lat': 'mean',
            'stop_lon': 'mean',
        })
        stops_df.columns = ['stop_id', 'original_stop_id', 'stop_lat', 'stop_lon']
        stops_df.reset_index(inplace=True)

        mask = stops_df['stop_id'] != stops_df['original_stop_id']
        stop_id_mapping = pd.Series(data=stops_df.loc[mask, 'stop_id'].values,
                                    index=stops_df.loc[mask, 'original_stop_id'].values)
        stop_id_mapping.sort_index(inplace=True)

        stops_df = stops_df[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']]
        stops_df.set_index('stop_id', inplace=True)

        return stops_df, stop_id_offset, stop_id_mapping

    def _merge_perons_df(self, perons_df_1: pd.DataFrame, perons_df_2: pd.DataFrame,
                         stop_id_offset: int, stop_id_mapping: pd.Series) -> Tuple[pd.DataFrame, int]:
        peron_id_offset = perons_df_1.index.max()

        perons_df_2.reset_index(inplace=True)
        perons_df_2.loc[:, 'peron_id'] += peron_id_offset
        perons_df_2.loc[:, 'stop_id'] = self._map_stop_id(perons_df_2['stop_id'], stop_id_offset, stop_id_mapping)
        perons_df_2.set_index('peron_id', inplace=True)

        perons_df = perons_df_1.append(perons_df_2)
        return perons_df, peron_id_offset

    def _merge_stop_times_df(self, stop_times_df_1: pd.DataFrame, stop_times_df_2: pd.DataFrame,
                             service_id_offset: int, stop_id_offset: int, stop_id_mapping: pd.Series,
                             peron_id_offset: int) -> pd.DataFrame:
        stop_times_df_2.reset_index(inplace=True)
        stop_times_df_2.loc[:, 'service_id'] += service_id_offset
        stop_times_df_2.loc[:, 'stop_id'] = self._map_stop_id(stop_times_df_2['stop_id'], stop_id_offset,
                                                              stop_id_mapping)
        stop_times_df_2.loc[:, 'peron_id'] += peron_id_offset
        stop_times_df_2.set_index(['service_id', 'block_id', 'trip_num', 'stop_sequence'], inplace=True)

        stop_times_df = stop_times_df_1.append(stop_times_df_2)
        return stop_times_df

    def _merge_transfers_df(self, transfers_df_1: pd.DataFrame, transfers_df_2: pd.DataFrame,
                            service_id_offset: int, stop_id_offset: int, stop_id_mapping: pd.Series,
                            peron_id_offset: int) -> pd.DataFrame:
        transfers_df_2.loc[:, 'service_id'] += service_id_offset
        transfers_df_2.loc[:, 'start_stop_id'] = self._map_stop_id(transfers_df_2['start_stop_id'], stop_id_offset,
                                                                   stop_id_mapping)
        transfers_df_2.loc[:, 'end_stop_id'] = self._map_stop_id(transfers_df_2['end_stop_id'], stop_id_offset,
                                                                 stop_id_mapping)
        transfers_df_2.loc[:, 'start_peron_id'] += peron_id_offset
        transfers_df_2.loc[:, 'end_peron_id'] += peron_id_offset

        transfers_df = transfers_df_1.append(transfers_df_2)
        transfers_df.reset_index(drop=True, inplace=True)
        return transfers_df

    def _map_stop_id(self, original_stop_id: pd.Series, stop_id_offset: int, stop_id_mapping: pd.Series) -> pd.Series:
        original_stop_id += stop_id_offset
        stop_id = original_stop_id.map(stop_id_mapping)
        mask = stop_id.isna()
        stop_id.loc[mask] = original_stop_id[mask]
        return stop_id.astype(int)
