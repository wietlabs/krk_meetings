import pytest

from src.data_provider.utils import parse_time, parse_stop_id, parse_trip_id, parse_service_id, parse_route_id


def test_parse_stop_id():
    assert parse_stop_id('stop_1234_567890') == (1234, 567890)


def test_parse_trip_id():
    assert parse_trip_id('block_123_trip_45_service_67') == (123, 45, 67)


def test_parse_service_id():
    assert parse_service_id('service_12') == 12


def test_parse_route_id():
    assert parse_route_id('route_123') == 123


@pytest.mark.parametrize('gtfs_time, expected_int_time', [
    ('00:00:00', 0),
    ('00:00:01', 1),
    ('00:01:00', 1 * 60),
    ('01:00:00', 1 * 3600),
    ('12:34:56', 12 * 3600 + 34 * 60 + 56),
    ('23:59:59', 23 * 3600 + 59 * 60 + 59),
    ('24:00:00', 24 * 3600),
    ('24:00:01', 24 * 3600 + 1),
    ('25:00:00', 25 * 3600),
])
def test_parse_time(gtfs_time: str, expected_int_time: int) -> None:
    assert parse_time(gtfs_time) == expected_int_time
