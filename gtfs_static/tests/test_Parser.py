from pathlib import Path

import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from DataClasses.ParsedData import ParsedData
from gtfs_static.Parser import Parser
from gtfs_static.utils import parse_time


@pytest.fixture(scope='session')  # executed only once
def parsed_data() -> ParsedData:
    gtfs_dir_path = Path(__file__).parent / 'resources' / 'GTFS_TEST'
    parser = Parser()
    return parser.parse(gtfs_dir_path)


def test_parse_calendar_df(parsed_data: ParsedData) -> None:
    expected = pd.DataFrame([
        [3, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 0, 0, 0, 0],
        ],
        columns=['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']) \
        .set_index('service_id')
    actual = parsed_data.calendar_df
    assert_frame_equal(expected, actual, check_dtype=False)


def test_parse_routes_df(parsed_data: ParsedData) -> None:
    expected = pd.DataFrame([
        [7, '0'],
        [583, '139'],
        [612, '194'],
        [134, '501'],
        [143, '611'],
        [42, 'A'],
        ], columns=['route_id', 'route_short_name']).set_index('route_id')
    actual = parsed_data.routes_df
    assert_frame_equal(expected, actual, check_dtype=False)


def test_parse_trips_df(parsed_data: ParsedData) -> None:
    expected = pd.DataFrame([
        [1652, 2, 1, 612, 'Czerwone Maki P+R'],
        [1652, 3, 1, 612, 'Krowodrza Górka'],
        [1652, 4, 1, 612, 'Czerwone Maki P+R'],
        [337, 2, 3, 583, 'Mydlniki'],
        [337, 3, 3, 583, 'Kombinat'],
        [337, 4, 3, 583, 'Mydlniki'],
        [337, 5, 3, 583, 'Kombinat'],
        ], columns=['block_id', 'trip_num', 'service_id', 'route_id', 'trip_headsign']) \
        .set_index(['service_id', 'block_id', 'trip_num'])
    actual = parsed_data.trips_df
    assert_frame_equal(expected, actual, check_dtype=False)


def test_parse_stops_df(parsed_data: ParsedData) -> None:
    def avg(*xs: float) -> float:
        return sum(xs) / len(xs)

    expected = pd.DataFrame([
        [1626, 'AGH / UR', avg(50.064389, 50.062664), avg(19.924345, 19.923186)],
        [55, 'Plac Inwalidów', avg(50.068681, 50.069472), avg(19.925866, 19.926957)],
        [57, 'Czarnowiejska', avg(50.066172, 50.066574), avg(19.923052, 19.922154)],
        [1230, 'Chopina', 50.067551, 19.917338],
        [58, 'Kawiory', avg(50.068419, 50.068372, 50.068801), avg(19.913791, 19.912865, 19.91391)],
        [61, 'Miasteczko Studenckie AGH', avg(50.0697, 50.069923, 50.069619, 50.070321), avg(19.903701, 19.905468, 19.906581, 19.904225)],
        [60, 'Biprostal', avg(50.07351, 50.072412, 50.073446), avg(19.91368, 19.91522, 19.915894)],
        [544, 'Brücknera', avg(50.011982, 50.012561), avg(19.875804, 19.876017)],
        [1785, 'Petőfiego (nż)', avg(50.094152, 50.094174), avg(20.035397, 20.035502)],
        [1368, 'Rżąka', 50.006257, 20.0111],
        [475, 'Bieżanów', 50.017537, 20.068257],
        ], columns=['stop_id', 'stop_name', 'stop_lat', 'stop_lon']).set_index('stop_id').sort_index()
    actual = parsed_data.stops_df
    assert_frame_equal(expected, actual, check_dtype=False)


def test_parse_perons_df(parsed_data: ParsedData) -> None:
    expected = pd.DataFrame([
        [1626, 311101, 'AGH / UR', 50.064389, 19.924345],
        [1626, 311102, 'AGH / UR', 50.062664, 19.923186],
        [55, 7903, 'Plac Inwalidów', 50.068681, 19.925866],
        [55, 7904, 'Plac Inwalidów', 50.069472, 19.926957],
        [57, 8101, 'Czarnowiejska', 50.066172, 19.923052],
        [57, 8102, 'Czarnowiejska', 50.066574, 19.922154],
        [1230, 287801, 'Chopina', 50.067551, 19.917338],
        [58, 8202, 'Kawiory', 50.068419, 19.913791],
        [58, 8203, 'Kawiory', 50.068372, 19.912865],
        [58, 8204, 'Kawiory', 50.068801, 19.91391],
        [61, 8501, 'Miasteczko Studenckie AGH', 50.0697, 19.903701],
        [61, 8502, 'Miasteczko Studenckie AGH', 50.069923, 19.905468],
        [61, 8503, 'Miasteczko Studenckie AGH', 50.069619, 19.906581],
        [61, 8504, 'Miasteczko Studenckie AGH', 50.070321, 19.904225],
        [60, 8403, 'Biprostal', 50.07351, 19.91368],
        [60, 8404, 'Biprostal', 50.072412, 19.91522],
        [60, 8405, 'Biprostal', 50.073446, 19.915894],
        [544, 76501, 'Brücknera', 50.011982, 19.875804],
        [544, 76502, 'Brücknera', 50.012561, 19.876017],
        [1785, 319101, 'Petőfiego (nż)', 50.094152, 20.035397],
        [1785, 319102, 'Petőfiego (nż)', 50.094174, 20.035502],
        [1368, 304401, 'Rżąka', 50.006257, 20.01116],
        [475, 66701, 'Bieżanów', 50.017537, 20.068257],
        ], columns=['stop_id', 'peron_id', 'peron_name', 'peron_lat', 'peron_lon']) \
        .set_index('peron_id')
    actual = parsed_data.perons_df
    assert_frame_equal(expected, actual, check_dtype=False)


def test_parse_stop_times_df(parsed_data: ParsedData) -> None:
    expected = pd.DataFrame([
        [1652, 2, 1, parse_time('06:50:00'), 60, 8404, 7],
        [1652, 2, 1, parse_time('06:51:00'), 58, 8202, 8],
        [1652, 2, 1, parse_time('06:52:00'), 1230, 287801, 9],
        [1652, 2, 1, parse_time('06:53:00'), 57, 8101, 10],
        [1652, 2, 1, parse_time('06:55:00'), 1626, 311102, 11],
        [337, 2, 3, parse_time('04:52:00'), 57, 8102, 1],
        [337, 2, 3, parse_time('04:54:00'), 58, 8203, 2],
        [337, 2, 3, parse_time('04:55:00'), 61, 8502, 3],
        [337, 3, 3, parse_time('23:57:00'), 61, 8503, 12],
        [337, 3, 3, parse_time('23:59:00'), 1230, 287801, 13],
        [337, 3, 3, parse_time('24:00:00'), 57, 8101, 14],
        [337, 3, 3, parse_time('24:02:00'), 55, 7904, 15],
        ], columns=['block_id', 'trip_num', 'service_id', 'departure_time', 'stop_id', 'peron_id', 'stop_sequence']) \
        .set_index(['service_id', 'block_id', 'trip_num', 'stop_sequence']) \
        [['stop_id', 'peron_id', 'departure_time']]
    actual = parsed_data.stop_times_df
    assert_frame_equal(expected, actual, check_dtype=False)


def test_create_transfers_df(parsed_data: ParsedData) -> None:
    expected = pd.DataFrame([
        [1652, 2, 1, parse_time('06:50:00'), parse_time('06:51:00'), 60, 58, 8404, 8202, 7, 60],
        [1652, 2, 1, parse_time('06:51:00'), parse_time('06:52:00'), 58, 1230, 8202, 287801, 8, 60],
        [1652, 2, 1, parse_time('06:52:00'), parse_time('06:53:00'), 1230, 57, 287801, 8101, 9, 60],
        [1652, 2, 1, parse_time('06:53:00'), parse_time('06:55:00'), 57, 1626, 8101, 311102, 10, 120],
        [337, 2, 3, parse_time('04:52:00'), parse_time('04:54:00'), 57, 58, 8102, 8203, 1, 120],
        [337, 2, 3, parse_time('04:54:00'), parse_time('04:55:00'), 58, 61, 8203, 8502, 2, 60],
        [337, 3, 3, parse_time('23:57:00'), parse_time('23:59:00'), 61, 1230, 8503, 287801, 12, 120],
        [337, 3, 3, parse_time('23:59:00'), parse_time('24:00:00'), 1230, 57, 287801, 8101, 13, 60],
        [337, 3, 3, parse_time('24:00:00'), parse_time('24:02:00'), 57, 55, 8101, 7904, 14, 120],
        ], columns=['block_id', 'trip_num', 'service_id', 'start_time', 'end_time',
                    'start_stop_id', 'end_stop_id', 'start_peron_id', 'end_peron_id', 'stop_sequence', 'duration'])
    actual = parsed_data.transfers_df
    assert_frame_equal(expected, actual, check_dtype=False)
