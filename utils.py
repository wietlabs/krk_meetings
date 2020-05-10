def format_time(time_int: int) -> str:
    mm = time_int // 60 % 60
    hh = (time_int // (60 * 60)) % 24
    return f'{hh:02d}:{mm:02d}'
