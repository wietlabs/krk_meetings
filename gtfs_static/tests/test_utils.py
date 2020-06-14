import pytest

from gtfs_static.utils import parse_time, parse_stop_id, parse_trip_id, parse_service_id, parse_route_id


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
