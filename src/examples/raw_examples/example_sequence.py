from src.data_classes.SequenceQuery import SequenceQuery
from src.data_provider.FloydDataProvider import FloydDataProvider
from src.solver.FloydSolver import FloydConnectionSolver

if __name__ == "__main__":
    # floyd_data = DataProvider.parse_and_extract_floyd_data()
    floyd_data = FloydDataProvider.load_floyd_data()
    solver = FloydConnectionSolver(floyd_data)

    stops_to_visit = ['Biprostal', 'Kawiory', 'Czarnowiejska']
    start_stop_name = 'Wrocławska'
    end_stop_name = 'AGH / UR'
    query = SequenceQuery(start_stop_name, end_stop_name, stops_to_visit)

    sequence = solver.find_best_sequence(query)
    print(sequence)
