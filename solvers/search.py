import time

from DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from static_timetable_module.gtfs_static.utils import parse_time
from solvers.BfsSolver.BfsSolver import BfsSolver
from DataClasses.TransferQuery import TransferQuery
from utils import format_time
from Visualization import Visualization

if __name__ == '__main__':
    # parsed_data = DataProvider.parse_data()
    parsed_data = GtfsStaticDataProvider.load_parsed_data()
    # extracted_data = DataProvider.extract_data()
    extracted_data = GtfsStaticDataProvider.load_extracted_data()

    solver = BfsSolver(parsed_data)

    stops_df = parsed_data.stops_df

    def get_stop_id_by_name(stop_name: str) -> int:
        try:
            return stops_df.index[stops_df['stop_name'] == stop_name][0]
        except IndexError:
            raise Exception('Stop not found')

    # start_time = parse_time(input('Godzina odjazdu: '))
    # start_stop_id = get_stop_id_by_name(input('Przystanek początkowy: '))
    # end_stop_id = get_stop_id_by_name(input('Przystanek końcowy: '))

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

    query = TransferQuery(start_time, start_stop_id, end_stop_id)

    t1 = time.time()
    result = solver.find_connections(query)
    t2 = time.time()
    print(f'{t2-t1:.3f} s')

    result = result.join(stops_df, on='stop_id')
    result['time_formatted'] = result['time'].apply(format_time)
    result = result[['time_formatted', 'stop_name', 'stop_lat', 'stop_lon']]

    visualization = Visualization()
    visualization.draw_stops(extracted_data, node_color='gray', edge_color='gray')
    visualization.draw_result_path(result, color='blue')
    visualization.show()
