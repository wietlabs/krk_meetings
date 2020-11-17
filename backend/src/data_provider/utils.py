from typing import Tuple
from math import sin, cos, sqrt, atan2, radians
from src.config import WALKING_SPEED


def parse_stop_id(gtfs_stop_id: str) -> Tuple[int, int]:
    _, stop_id, peron_id = gtfs_stop_id.split('_', 2)
    return int(stop_id), int(peron_id)


def parse_trip_id(gtfs_trip_id: str) -> Tuple[int, int, int]:
    _, block_id, _, trip_num, _, service_id = gtfs_trip_id.split('_', 6)
    return int(block_id), int(trip_num), int(service_id)


def parse_service_id(gtfs_service_id: str) -> int:
    _, service_id = gtfs_service_id.split('_', 2)
    return int(service_id)


def parse_route_id(gtfs_route_id: str) -> int:
    _, route_id = gtfs_route_id.split('_', 2)
    return int(route_id)


def parse_time(gtfs_time: str) -> int:
    h, m, s = gtfs_time.split(':', 3)
    return int(s) + 60 * int(m) + 3600 * int(h)


def get_walking_distance(lon_1, lat_1, lon_2, lat_2) -> int:
    lon_1 = radians(lon_1)
    lon_2 = radians(lon_2)
    lat_1 = radians(lat_1)
    lat_2 = radians(lat_2)
    earth_radius = 6373000.0
    dlon = lon_2 - lon_1
    dlat = lat_2 - lat_1

    a = sin(dlat / 2) ** 2 + cos(lat_1) * cos(lat_2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = int(earth_radius * c)
    return distance


def get_walking_time(lon_1, lat_1, lon_2, lat_2) -> int:
    distance = get_walking_distance(lon_1, lat_1, lon_2, lat_2)
    walking_time = distance / WALKING_SPEED
    walking_time = round(walking_time)
    return walking_time


def is_nightly(route_name, nightly_route_ranges):
    try:
        route_number = int(route_name)
        for r in nightly_route_ranges:
            if r[0] <= route_number <= r[1]:
                return True
        return False
    except ValueError:
        return False
