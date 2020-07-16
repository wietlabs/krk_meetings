from DataClasses.MeetingQuery import MeetingQuery
from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from development.DataProviders.DataProvider import DataProvider
from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.FloydSolver.FloydSolver import FloydSolver

if __name__ == "__main__":
    # floyd_data = DataProvider.parse_and_extract_floyd_data()
    floyd_data = DataProvider.load_floyd_data()
    solver = FloydSolver(floyd_data)

    start_stop_names = ['Azory', 'Kawiory', 'Rondo Mogilskie']
    query = MeetingQuery(start_stop_names, 'square')

    meeting_points = solver.find_meeting_points(query)
    print(meeting_points)
