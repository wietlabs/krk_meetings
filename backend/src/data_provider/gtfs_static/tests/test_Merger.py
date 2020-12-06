import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

from src.data_provider.gtfs_static.Merger import Merger


def test_merge_stops_df() -> None:
    stops_df_1 = pd.DataFrame([
        [1, 'Aaa', 50.0, 20.0],
        [2, 'Bbb', 51.0, 21.0],
        [4, 'Ccc', 52.0, 22.0],
        [5, 'Eee', 54.0, 24.0],
    ], columns=['stop_id', 'stop_name', 'stop_lat', 'stop_lon']).set_index('stop_id')

    stops_df_2 = pd.DataFrame([
        [1, 'Aaa', 50.2, 20.2],
        [3, 'Bbb', 51.2, 21.2],
        [4, 'Ddd', 53.2, 23.2],
        [6, 'Fff', 55.2, 25.2],
    ], columns=['stop_id', 'stop_name', 'stop_lat', 'stop_lon']).set_index('stop_id')

    merger = Merger()
    actual_stops_df, actual_stop_id_offset, actual_stop_id_mapping = merger._merge_stops_df(stops_df_1, stops_df_2)

    expected_stops_df = pd.DataFrame([
        [1, 'Aaa', 50.1, 20.1],
        [2, 'Bbb', 51.1, 21.1],
        [4, 'Ccc', 52.0, 22.0],
        [9, 'Ddd', 53.2, 23.2],
        [5, 'Eee', 54.0, 24.0],
        [11, 'Fff', 55.2, 25.2],
    ], columns=['stop_id', 'stop_name', 'stop_lat', 'stop_lon']).set_index('stop_id')

    expected_stop_id_mapping = pd.Series([1, 2], index=[6, 8])

    assert_frame_equal(actual_stops_df, expected_stops_df)
    assert_series_equal(actual_stop_id_mapping, expected_stop_id_mapping)
    assert actual_stop_id_offset == 5
