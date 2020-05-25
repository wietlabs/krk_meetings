from DataClasses.SequenceQuery import SequenceQuery
from DataProviders.GraphDataProvider import GraphDataProvider
from DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.FloydSolver.FloydSolver import FloydSolver

if __name__ == "__main__":
    #gtfs_data = GtfsStaticDataProvider.extract_data()
    #print("GTFS DATA EXTRACTED")
    #graph_data = GraphDataProvider.extract_data(gtfs_data)
    #print("GRAPH DATA EXTRACTED")
    graph_data = GraphDataProvider.load_data()
    solver = FloydSolver(graph_data)
    stops_to_visit = ['Biprostal', 'Kawiory', 'Czarnowiejska']
    start_stop_name = 'Wrocławska'
    end_stop_name = 'AGH / UR'
    query = SequenceQuery(start_stop_name, end_stop_name, stops_to_visit)
    sequence = solver.find_optimal_sequence(query)
    print(sequence)
