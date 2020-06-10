import datetime
import time

from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.BfsSolver.BfsSolver import BfsSolver
from DataClasses.TransferQuery import TransferQuery


if __name__ == '__main__':
    # parsed_data = GtfsStaticDataProvider.parse_data()
    # extracted_data = GtfsStaticDataProvider.extract_data()
    parsed_data = GtfsStaticDataProvider.load_parsed_data()
    extracted_data = GtfsStaticDataProvider.load_extracted_data()

    stops_df = parsed_data.stops_df

    solver = BfsSolver(parsed_data, extracted_data)

    def search(start_date: datetime.date, start_time: datetime.time, start_stop_name: str, end_stop_name: str):
        query = TransferQuery(start_date, start_time, start_stop_name, end_stop_name)

        t1 = time.time()
        results = solver.find_connections(query)
        t2 = time.time()
        print(f'{t2 - t1:.3f} s')

        # TODO: visualize results
        # result = result.join(stops_df, on='stop_id')
        # result['time_formatted'] = result['time'].apply(format_time)
        # result = result[['time_formatted', 'stop_name', 'stop_lat', 'stop_lon']]
        #
        # visualization = Visualization()
        # visualization.draw_stops(extracted_data, node_color='gray', edge_color='gray')
        # visualization.draw_result_path(result, color='blue')
        # visualization.show()

    today = datetime.datetime.now().date()

    search(today, datetime.time(6, 3), 'Miasteczko Studenckie AGH', 'Dworzec Główny Wschód')
    search(today, datetime.time(21, 20), 'Brzeźnica Dworzec', 'Słomniki Osiedle')
    search(today, datetime.time(6, 58), 'Wieliczka Miasto', 'Górka Narodowa Wschód')
    search(today, datetime.time(22, 10), 'Goszcza Dworek', 'Grabie Pętla')

    # start_time = datetime.datetime.strptime(input('Godzina odjazdu: '), '%H:%M').time()
    # start_stop_name = input('Przystanek początkowy: ')
    # end_stop_name = input('Przystanek końcowy: ')
    # search(today, start_time, start_stop_name, end_stop_name)
