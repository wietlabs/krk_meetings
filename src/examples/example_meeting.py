from src.data_classes.MeetingQuery import MeetingQuery
from src.data_provider.FloydDataProvider import DataProvider
from src.solver.FloydSolver import FloydConnectionSolver

if __name__ == "__main__":
    floyd_data = DataProvider.parse_and_extract_floyd_data()
    # floyd_data = DataProvider.load_floyd_data()
    solver = FloydConnectionSolver(floyd_data)

    start_stop_names = ['Azory', 'Kawiory', 'Rondo Mogilskie']
    query = MeetingQuery(start_stop_names, 'square')

    meeting_points = solver.find_meeting_points(query)
    print(meeting_points)
