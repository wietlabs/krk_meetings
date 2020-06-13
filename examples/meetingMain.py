from src.DataClasses.MeetingQuery import MeetingQuery
from src.DataConverters.DataProvider import DataProvider
from src.Solvers.FloydSolver import FloydSolver

if __name__ == "__main__":
    #parsed_data = DataProvider.parse_data()
    #print("DATA PARSED")
    #extracted_data = DataProvider.extract_data(parsed_data)
    #print("DATA EXTRACTED")
    extracted_data = DataProvider.load_extracted_data()
    floyd_solver_data = DataProvider.extract_floyd_solver_data(extracted_data)
    print("FLOYD DATA EXTRACTED")
    #floyd_solver_data = DataProvider.load_floyd_solver_data()
    solver = FloydSolver(floyd_solver_data)
    start_stop_names = ['Azory', 'Kawiory', 'Rondo Mogilskie']
    query = MeetingQuery(start_stop_names, 'square')
    meeting_points = solver.find_meeting_points(query)
    print(meeting_points)
