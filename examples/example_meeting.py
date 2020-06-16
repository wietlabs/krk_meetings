from DataClasses.MeetingQuery import MeetingQuery
from development.DataProviders.GraphDataProvider import GraphDataProvider
from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.FloydSolver.FloydSolver import FloydSolver

if __name__ == "__main__":
    # gtfs_data = GtfsStaticDataProvider.extract_data()
    # graph_data = GraphDataProvider.extract_data(gtfs_data)

    graph_data = GraphDataProvider.load_data()
    solver = FloydSolver(graph_data)

    start_stop_names = ['Azory', 'Kawiory', 'Rondo Mogilskie']
    query = MeetingQuery(start_stop_names, 'square')

    meeting_points = solver.find_meeting_points(query)
    print(meeting_points)
