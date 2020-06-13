from DataClasses.TransferQuery import TransferQuery
from development.DataProviders.GraphDataProvider import GraphDataProvider
from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.FloydSolver.FloydSolver import FloydSolver
from datetime import date, time

if __name__ == "__main__":
    #gtfs_data = GtfsStaticDataProvider.extract_data()
    #print("GTFS DATA EXTRACTED")
    #graph_data = GraphDataProvider.extract_data(gtfs_data)
    #print("GRAPH DATA EXTRACTED")
    graph_data = GraphDataProvider.load_data()
    parsed_data = GtfsStaticDataProvider.load_parsed_data()
    floydSolver = FloydSolver(graph_data)

    start_time = time(20, 0, 0)
    start_date = date(2020, 5, 24)
    start_stop_name = 'Czerwone Maki P+R'
    end_stop_name = 'Kombinat'
    query = TransferQuery(start_date, start_time, start_stop_name, end_stop_name)
    connections = floydSolver.find_connections(query)

    for connection in connections:
        print(connection)
        print('-' * 30)
