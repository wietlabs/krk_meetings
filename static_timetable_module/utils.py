from typing import Tuple


def parse_stop_id(gtfs_stop_id: str) -> Tuple[int, int]:
    _, stop_id, peron_id = gtfs_stop_id.split('_', 2)
    return int(stop_id), int(peron_id)


def parse_trip_id(gtfs_trip_id: str) -> Tuple[int, int, int]:
    _, block_id, _, trip_num, _, service_id = gtfs_trip_id.split('_', 6)
    return int(block_id), int(trip_num), int(service_id)


def parse_service_id(gtfs_service_id: str) -> int:
    _, service_id = gtfs_service_id.split('_', 2)
    return int(service_id)


def parse_time(gtfs_time: str) -> int:
    h, m, s = gtfs_time.split(':', 3)
    return int(s) + 60*int(m) + 3600*int(h)
