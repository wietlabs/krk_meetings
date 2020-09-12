from src.data_classes.MeetingQuery import MeetingQuery
from src.data_provider.FloydDataProvider import FloydDataProvider
from src.solver.FloydSolver import FloydSolver

if __name__ == "__main__":
    # floyd_data = DataProvider.parse_and_extract_floyd_data()
    floyd_data = FloydDataProvider.load_floyd_data()
    solver = FloydSolver(floyd_data)

    start_stop_names = ['Azory', 'Kawiory', 'Rondo Mogilskie']
    query = MeetingQuery(start_stop_names, 'square')

    meeting_points = solver.find_meeting_points(query)
    print(meeting_points)
