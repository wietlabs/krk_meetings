def format_time(time_int: int) -> str:
    mm = time_int // 60 % 60
    hh = (time_int // (60 * 60)) % 24
    return f'{hh:02d}:{mm:02d}'


def time_to_string(time):
    h = str(int(time / 3600))
    m = str(int(time % 3600 / 60))
    s = str(int(time % 60))
    if len(m) == 1: m = '0' + m
    if len(s) == 1: s = '0' + s
    return h + ':' + m + ':' + s
