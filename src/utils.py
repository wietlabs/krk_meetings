from datetime import time, date, timedelta


def format_time(time_int: int) -> str:
    mm = time_int // 60 % 60
    hh = (time_int // (60 * 60)) % 24
    return f'{hh:02d}:{mm:02d}'


def time_to_int(t: time):
    result = t.hour * 3600 + t.minute * 60 + t.second
    return result


def int_to_time(t: int):
    h = int(t % 86400 / 3600)
    m = int(t % 3600 / 60)
    s = int(t % 60)
    result = time(h, m, s)
    return result


def shift_date(d: date, t: int):
    shift = int(t / 86400)
    return d + timedelta(days=shift)
