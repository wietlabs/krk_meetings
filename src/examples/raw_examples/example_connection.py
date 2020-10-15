from datetime import date, time

from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_provider.FloydDataProvider import FloydDataProvider
from src.solver.FloydSolver import FloydSolver

if __name__ == "__main__":
    floyd_data = FloydDataProvider.load_floyd_data()
    solver = FloydSolver(floyd_data)

    start_date = date(2020, 5, 24)
    start_time = time(20, 0, 0)
    start_stop_name = 'Teatr Słowackiego'
    end_stop_name = 'Kurdwanów P+R'

    query = ConnectionQuery(start_date, start_time, start_stop_name, end_stop_name)
    connections = solver.find_connections(query)

    for connection in connections:
        print(connection)
        print('-' * 30)
