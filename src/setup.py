from src.data_provider.FloydDataProvider import DataProvider
from src.solver.ConnectionSolver import ConnectionSolver
from multiprocessing import Process

if __name__ == "__main__":
    data_provider = DataProvider()
    connection_solver = ConnectionSolver()
    data_provider_process = Process(target=data_provider.start())
    connection_solver_process = Process(target=connection_solver.start())
    print("blocking")
    data_provider_process.start()
    print("non blocking")
    connection_solver.start()
    print("non blocking")
