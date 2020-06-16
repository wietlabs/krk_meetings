from datetime import date, time

from DataClasses.TransferQuery import TransferQuery
from development.DataProviders.GraphDataProvider import GraphDataProvider
from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.FloydSolver.FloydSolver import FloydSolver

if __name__ == "__main__":
    # gtfs_data = GtfsStaticDataProvider.extract_data()
    # graph_data = GraphDataProvider.extract_data(gtfs_data)

    graph_data = GraphDataProvider.load_data()
    solver = FloydSolver(graph_data)

    start_date = date(2020, 5, 24)
    start_time = time(20, 0, 0)
    start_stop_name = 'Krzeszowice Dworzec Autobusowy'
    end_stop_name = 'Boleń Pętla'

    query = TransferQuery(start_date, start_time, start_stop_name, end_stop_name)
    connections = solver.find_connections(query)

    for connection in connections:
        print(connection)
        print('-' * 30)
