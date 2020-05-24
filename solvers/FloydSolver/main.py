from DataClasses.TransferQuery import TransferQuery
from DataProviders.GraphDataProvider import GraphDataProvider
from DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.FloydSolver.FloydSolver import FloydSolver
from datetime import date, time

if __name__ == "__main__":
    #gtfs_data = GtfsStaticDataProvider.extract_data()
    #print("GTFS DATA EXTRACTED")
    #graph_data = GraphDataProvider.extract_data(gtfs_data)
    #print("GRAPH DATA EXTRACTED")
    graph_data = GraphDataProvider.load_data()
    solver = FloydSolver(graph_data)
    start_time = time(20, 0, 0)
    start_date = date(2020, 5, 24)
    start_stop_name = 'Czerwone Maki P+R'
    end_stop_name = 'Kombinat'
    query = TransferQuery(start_date, start_time, start_stop_name, end_stop_name)
    connections = solver.get_connections(query)
    for connection in connections:
        for transfer in connection:
            print(str(transfer))
        print("------------------------------")



















