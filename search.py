import time
from pathlib import Path

from static_timetable_module.gtfs_static.ParsedData import ParsedData
from static_timetable_module.gtfs_static.utils import parse_time
from solvers.BasicSolver import BasicSolver
from solvers.Query import Query
from utils import format_time
from Visualization import Visualization

if __name__ == '__main__':
    tmp_dir = Path(__file__).parent / 'static_timetable_module' / 'gtfs_static' / 'tmp'
    parsed_data = ParsedData.load(tmp_dir / 'parsed_data.pickle')
    extracted_data = ParsedData.load(tmp_dir / 'extracted_data.pickle')

    solver = BasicSolver(parsed_data)

    stops_df = parsed_data.stops_df

    def get_stop_id_by_name(stop_name: str) -> int:
        try:
            return stops_df.index[stops_df['stop_name'] == stop_name][0]
        except IndexError:
            raise Exception('Stop not found')

    start_time = parse_time('06:03:00')
    start_stop_id = get_stop_id_by_name('Miasteczko Studenckie AGH')
    end_stop_id = get_stop_id_by_name('Dworzec Główny Wschód')

    # start_time = parse_time('21:20:00')
    # start_stop_id = get_stop_id_by_name('Brzeźnica Dworzec')
    # end_stop_id = get_stop_id_by_name('Słomniki Osiedle')

    # start_time = parse_time('06:58:00')
    # start_stop_id = get_stop_id_by_name('Wieliczka Miasto')
    # end_stop_id = get_stop_id_by_name('Górka Narodowa Wschód')

    # start_time = parse_time('22:10:00')
    # start_stop_id = get_stop_id_by_name('Goszcza Dworek')
    # end_stop_id = get_stop_id_by_name('Grabie Pętla')

    query = Query(start_time, start_stop_id, end_stop_id)

    t1 = time.time()
    result = solver.find_connection(query)
    t2 = time.time()
    print(f'\nFound in {t2-t1:.3f} s')

    result['time_formatted'] = result['time'].apply(format_time)
    result = result[['time_formatted', 'stop_name', 'stop_lat', 'stop_lon']]

    visualization = Visualization()
    visualization.draw_stops(extracted_data, node_color='gray', edge_color='gray')
    visualization.draw_result_path(result, color='blue')
    visualization.show()

    pass  # set breakpoint here
