from DataClasses.SequenceQuery import SequenceQuery
from development.DataProviders.GraphDataProvider import GraphDataProvider
from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.FloydSolver.FloydSolver import FloydSolver

if __name__ == "__main__":
    # gtfs_data = GtfsStaticDataProvider.extract_data()
    # graph_data = GraphDataProvider.extract_data(gtfs_data)

    graph_data = GraphDataProvider.load_data()
    solver = FloydSolver(graph_data)

    stops_to_visit = ['Biprostal', 'Kawiory', 'Czarnowiejska']
    start_stop_name = 'Wrocławska'
    end_stop_name = 'AGH / UR'
    query = SequenceQuery(start_stop_name, end_stop_name, stops_to_visit)

    sequence = solver.find_optimal_sequence(query)
    print(sequence)
