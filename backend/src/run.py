from src.data_provider.DataProvider import start_data_provider
from src.server.BackendServer import start_flask_server
from src.rabbitmq.RmqConnectionSolver import start_connection_solver
from src.rabbitmq.RmqMeetingSolver import start_meeting_solver
from src.rabbitmq.RmqSequenceSolver import start_sequence_solver
import multiprocessing


CONNECTION_SOLVER_INSTANCES = 2
MEETING_SOLVER_INSTANCES = 1
SEQUENCE_SOLVER_INSTANCES = 1


def run():
    data_provider_process = multiprocessing.Process(target=start_data_provider)
    connection_solver_processes = [
        multiprocessing.Process(target=start_connection_solver) for _ in range(CONNECTION_SOLVER_INSTANCES)]
    meeting_solver_processes = [
        multiprocessing.Process(target=start_meeting_solver) for _ in range(MEETING_SOLVER_INSTANCES)]
    sequence_solver_processes = [
        multiprocessing.Process(target=start_sequence_solver) for _ in range(SEQUENCE_SOLVER_INSTANCES)]
    flask_server_process = multiprocessing.Process(target=start_flask_server)
    data_provider_process.start()
    for process in connection_solver_processes:
        process.start()
    for process in meeting_solver_processes:
        process.start()
    for process in sequence_solver_processes:
        process.start()
    flask_server_process.start()


if __name__ == "__main__":
    run()
