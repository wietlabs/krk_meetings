import time
from pathlib import Path
from static_timetable_module.gtfs_static.ParsedData import ParsedData
from static_timetable_module.gtfs_static.utils import parse_time
from solvers.BasicSolver import BasicSolver
from solvers.Query import Query
from utils import format_time

if __name__ == '__main__':
    path = Path(__file__).parent / 'static_timetable_module' / 'gtfs_static' / 'tmp' / 'parsed_data.pickle'
    parsed_data = ParsedData.load(path)
    stops_df = parsed_data.stops_df

    def get_stop_id_by_name(stop_name: str) -> int:
        try:
            return stops_df.index[stops_df['stop_name'] == stop_name][0]
        except IndexError:
            raise Exception('Stop not found')

    start_time = parse_time('06:03:00')
    start_stop_id = get_stop_id_by_name('Miasteczko Studenckie AGH')
    end_stop_id = get_stop_id_by_name('Dworzec Główny Wschód')

    query = Query(start_time, start_stop_id, end_stop_id)

    solver = BasicSolver(parsed_data)

    t1 = time.time()
    result = solver.find_connection(query)
    t2 = time.time()

    result['time_formatted'] = result['time'].apply(format_time)
    result = result[['time_formatted', 'stop_name', 'stop_lat', 'stop_lon']]

    print(f'\nFound in {t2-t1:.3f} s')
    print(result)
