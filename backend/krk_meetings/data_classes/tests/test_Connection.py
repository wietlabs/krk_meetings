from datetime import date, time, datetime, timedelta

import pytest

from krk_meetings.data_classes.Connection import Connection
from krk_meetings.data_classes.Transfer import Transfer

connection1 = Connection([
    Transfer('139', 'headsign', 'Czarnowiejska', 'Miasteczko Studenckie AGH', datetime(2019, 1, 1, 12, 34), datetime(2019, 1, 1, 12, 37), 0, []),
])

connection2 = Connection([
    Transfer('139', 'headsign', 'Czarnowiejska', 'Miasteczko Studenckie AGH', datetime(2019, 12, 31, 23, 59), datetime(2020, 1, 1, 0, 1), 0, []),
])

connection3 = Connection([
    Transfer('139', 'headsign', 'Czarnowiejska', 'Plac Inwalidów', datetime(2020, 6, 13, 13, 3), datetime(2020, 6, 13, 13, 6), 0, []),
    Transfer('179', 'headsign', 'Plac Inwalidów', 'Jubilat', datetime(2020, 6, 13, 13, 7), datetime(2020, 6, 13, 13, 12), 0, []),
    Transfer('252', 'headsign', 'Jubilat', 'Kraków Airport', datetime(2020, 6, 13, 13, 14), datetime(2020, 6, 13, 13, 40), 0, []),
])


@pytest.mark.parametrize('connection, expected_transfers_count', [
    (connection1, 1),
    (connection2, 1),
    (connection3, 3),
])
def test_departure_time(connection: Connection, expected_transfers_count: int) -> None:
    assert connection.transfers_count == expected_transfers_count


@pytest.mark.parametrize('connection, expected_departure_time', [
    (connection1, datetime(2019, 1, 1, 12, 34)),
    (connection2, datetime(2019, 12, 31, 23, 59)),
    (connection3, datetime(2020, 6, 13, 13, 3)),
])
def test_departure_time(connection: Connection, expected_departure_time: datetime) -> None:
    assert connection.departure_time() == expected_departure_time


@pytest.mark.parametrize('connection, expected_arrival_time', [
    (connection1, datetime(2019, 1, 1, 12, 37)),
    (connection2, datetime(2020, 1, 1, 0, 1)),
    (connection3, datetime(2020, 6, 13, 13, 40)),
])
def test_arrival_time(connection: Connection, expected_arrival_time: datetime) -> None:
    assert connection.arrival_time() == expected_arrival_time


@pytest.mark.parametrize('connection, expected_duration', [
    (connection1, timedelta(seconds=3 * 60)),
    (connection2, timedelta(seconds=2 * 60)),
    (connection3, timedelta(seconds=37 * 60)),
])
def test_duration(connection: Connection, expected_duration: timedelta) -> None:
    assert connection.duration() == expected_duration
