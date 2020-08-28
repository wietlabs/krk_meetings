from datetime import date, time, datetime, timedelta

import pytest

from src.data_classes.ConnectionResults import ConnectionResults
from src.data_classes.Transfer import Transfer

connection1 = ConnectionResults([
    Transfer('139', 'Czarnowiejska', 'Miasteczko Studenckie AGH', date(2019, 1, 1), time(12, 34), date(2019, 1, 1), time(12, 37)),
])

connection2 = ConnectionResults([
    Transfer('611', 'Czarnowiejska', 'Miasteczko Studenckie AGH', date(2019, 12, 31), time(23, 59), date(2020, 1, 1), time(0, 1)),
])

connection3 = ConnectionResults([
    Transfer('139', 'Czarnowiejska', 'Plac Inwalidów', date(2020, 6, 13), time(13, 3), date(2020, 6, 13), time(13, 6)),
    Transfer('179', 'Plac Inwalidów', 'Jubilat', date(2020, 6, 13), time(13, 7), date(2020, 6, 13), time(13, 12)),
    Transfer('252', 'Jubilat', 'Kraków Airport', date(2020, 6, 13), time(13, 14), date(2020, 6, 13), time(13, 40)),
])


@pytest.mark.parametrize('connection, expected_transfers_count', [
    (connection1, 1),
    (connection2, 1),
    (connection3, 3),
])
def test_departure_time(connection: ConnectionResults, expected_transfers_count: int) -> None:
    assert connection.transfers_count() == expected_transfers_count


@pytest.mark.parametrize('connection, expected_departure_time', [
    (connection1, datetime(2019, 1, 1, 12, 34)),
    (connection2, datetime(2019, 12, 31, 23, 59)),
    (connection3, datetime(2020, 6, 13, 13, 3)),
])
def test_departure_time(connection: ConnectionResults, expected_departure_time: datetime) -> None:
    assert connection.departure_time() == expected_departure_time


@pytest.mark.parametrize('connection, expected_arrival_time', [
    (connection1, datetime(2019, 1, 1, 12, 37)),
    (connection2, datetime(2020, 1, 1, 0, 1)),
    (connection3, datetime(2020, 6, 13, 13, 40)),
])
def test_arrival_time(connection: ConnectionResults, expected_arrival_time: datetime) -> None:
    assert connection.arrival_time() == expected_arrival_time


@pytest.mark.parametrize('connection, expected_duration', [
    (connection1, timedelta(seconds=3 * 60)),
    (connection2, timedelta(seconds=2 * 60)),
    (connection3, timedelta(seconds=37 * 60)),
])
def test_duration(connection: ConnectionResults, expected_duration: timedelta) -> None:
    assert connection.duration() == expected_duration
