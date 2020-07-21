from datetime import date, time

from DataClasses.TransferQuery import TransferQuery
from development.DataProviders.DataProvider import DataProvider
from solvers.FloydSolver.FloydSolver import FloydSolver

if __name__ == "__main__":
    #floyd_data = DataProvider.parse_and_extract_floyd_data()
    floyd_data = DataProvider.load_floyd_data()
    solver = FloydSolver(floyd_data)

    start_date = date(2020, 5, 24)
    start_time = time(20, 0, 0)
    start_stop_name = 'Teatr Słowackiego'
    end_stop_name = 'Kurdwanów P+R'

    query = TransferQuery(start_date, start_time, start_stop_name, end_stop_name)
    connections = solver.find_connections(query)

    for connection in connections:
        print(connection)
        print('-' * 30)
