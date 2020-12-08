from src.data_provider.DelaysProvider import start_delays_provider
from src.data_provider.DataProvider import start_data_provider
from src.server.BackendServer import start_flask_server
from src.rabbitmq.RmqConnectionSolver import start_connection_solver
from src.rabbitmq.RmqMeetingSolver import start_meeting_solver
from src.rabbitmq.RmqSequenceSolver import start_sequence_solver
import multiprocessing


def run(connection_solver_instances=1, meeting_solver_instances=1, sequence_solver_instances=1):
    data_provider_process = multiprocessing.Process(target=start_data_provider)
    delays_provider_process = multiprocessing.Process(target=start_delays_provider)
    connection_solver_processes = [
        multiprocessing.Process(target=start_connection_solver) for _ in range(connection_solver_instances)]
    meeting_solver_processes = [
        multiprocessing.Process(target=start_meeting_solver) for _ in range(meeting_solver_instances)]
    sequence_solver_processes = [
        multiprocessing.Process(target=start_sequence_solver) for _ in range(sequence_solver_instances)]
    flask_server_process = multiprocessing.Process(target=start_flask_server)

    flask_server_process.start()
    delays_provider_process.start()
    data_provider_process.start()
    for process in connection_solver_processes:
        process.start()
    for process in meeting_solver_processes:
        process.start()
    for process in sequence_solver_processes:
        process.start()


if __name__ == "__main__":
    run()
