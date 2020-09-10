from src.data_provider.FloydDataProvider import start_data_provider
from src.server.FlaskServer import start_flask_server
from src.solver.ConnectionSolver import start_connection_solver
from src.solver.MeetingSolver import start_meeting_solver
from src.solver.SequenceSolver import start_sequence_solver
import multiprocessing


def setup():
    data_provider_process = multiprocessing.Process(target=start_data_provider)
    connection_solver_process = multiprocessing.Process(target=start_connection_solver)
    meeting_solver_process = multiprocessing.Process(target=start_meeting_solver)
    sequence_solver_process = multiprocessing.Process(target=start_sequence_solver)
    flask_server_process = multiprocessing.Process(target=start_flask_server)
    data_provider_process.start()
    connection_solver_process.start()
    meeting_solver_process.start()
    sequence_solver_process.start()
    flask_server_process.start()


if __name__ == "__main__":
    setup()