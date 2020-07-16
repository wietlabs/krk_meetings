from DataClasses.SequenceQuery import SequenceQuery
from development.DataProviders.DataProvider import DataProvider
from solvers.FloydSolver.FloydSolver import FloydSolver

if __name__ == "__main__":
    # floyd_data = DataProvider.parse_and_extract_floyd_data()
    floyd_data = DataProvider.load_floyd_data()
    solver = FloydSolver(floyd_data)

    stops_to_visit = ['Biprostal', 'Kawiory', 'Czarnowiejska']
    start_stop_name = 'Wrocławska'
    end_stop_name = 'AGH / UR'
    query = SequenceQuery(start_stop_name, end_stop_name, stops_to_visit)

    sequence = solver.find_optimal_sequence(query)
    print(sequence)
