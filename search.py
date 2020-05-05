import time
from pathlib import Path
from static_timetable_module.gtfs_static.ParsedData import ParsedData
from static_timetable_module.gtfs_static.utils import parse_time
from solvers.BasicSolver import BasicSolver
from solvers.Query import Query


if __name__ == '__main__':
    path = Path(__file__).parent / 'static_timetable_module' / 'gtfs_static' / 'tmp' / 'parsed_data.pickle'
    parsed_data = ParsedData.load(path)

    def get_stop_id_by_name(stop_name: str) -> int:
        df = parsed_data.stops_df
        return df.index[df['stop_name'] == stop_name][0]

    start_time = parse_time('06:03:00')
    start_stop_id = get_stop_id_by_name('Miasteczko Studenckie AGH')
    end_stop_id = get_stop_id_by_name('Dworzec Główny Wschód')

    query = Query(start_time, start_stop_id, end_stop_id)

    solver = BasicSolver(parsed_data)

    t1 = time.time()
    result = solver.find_connection(query)
    t2 = time.time()

    def format_time(time_int: int) -> str:
        mm = time_int // 60 % 60
        hh = (time_int // (60 * 60)) % 24
        return f'{hh:02d}:{mm:02d}'

    for stop_id, time in result:
        time_str = format_time(time)
        stop_name = parsed_data.stops_df.loc[stop_id, 'stop_name']
        print(time_str, stop_name)

    print(f'\nFound in {t2-t1:.3f} s')
