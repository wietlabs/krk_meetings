import datetime
import time

from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from src.Solvers.BfsSolver import BfsSolver
from src.DataClasses.TransferQuery import TransferQuery
from src.DataClasses.BfsSolverData import BfsSolverData


if __name__ == '__main__':
    # parsed_data = GtfsStaticDataProvider.parse_data()
    # extracted_data = GtfsStaticDataProvider.extract_data()
    parsed_data = GtfsStaticDataProvider.load_parsed_data()
    extracted_data = GtfsStaticDataProvider.load_extracted_data()

    bfs_solver_data = BfsSolverData.create(parsed_data, extracted_data)
    solver = BfsSolver(bfs_solver_data)

    # start_time = datetime.datetime.strptime(input('Godzina odjazdu: '), '%H:%M').time()
    # start_stop_name = input('Przystanek początkowy: ')
    # end_stop_name = input('Przystanek końcowy: ')

    # start_time = datetime.time(6, 3)
    # start_stop_name = 'Miasteczko Studenckie AGH'
    # end_stop_name = 'Dworzec Główny Wschód'

    start_time = datetime.time(21, 20)
    start_stop_name = 'Brzeźnica Dworzec'
    end_stop_name = 'Słomniki Osiedle'

    # start_time = datetime.time(6, 58)
    # start_stop_name = 'Wieliczka Miasto'
    # end_stop_name = 'Górka Narodowa Wschód'

    # start_time = datetime.time(22, 10)
    # start_stop_name = 'Goszcza Dworek'
    # end_stop_name = 'Grabie Pętla'

    start_date = datetime.datetime.now().date()
    query = TransferQuery(start_date, start_time, start_stop_name, end_stop_name)

    t1 = time.time()
    results = solver.find_connections(query)
    t2 = time.time()
    print(f'{t2 - t1:.3f} s')

    connection = results[0]
    print(connection)

    # TODO: visualize results
    # result = result.join(stops_df, on='stop_id')
    # result['time_formatted'] = result['time'].apply(format_time)
    # result = result[['time_formatted', 'stop_name', 'stop_lat', 'stop_lon']]
    #
    # visualization = Visualization()
    # visualization.draw_stops(extracted_data, node_color='gray', edge_color='gray')
    # visualization.draw_result_path(result, color='blue')
    # visualization.show()
