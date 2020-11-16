from src.data_classes.ConnectionResults import ConnectionResults
from src.exchanges import EXCHANGES
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.solver.ConnectionSolver import ConnectionSolver


def start_connection_solver():
    connection_solver = RmqConnectionSolver()
    connection_solver.start()


class RmqConnectionSolver:
    def __init__(self):
        self.connection_solver = ConnectionSolver()
        self.query_consumer = RmqConsumer(EXCHANGES.CONNECTION_QUERY.value, self.consume_query)
        self.results_producer = RmqProducer(EXCHANGES.FLASK_SERVER_CONNECTION.value)

    def start(self):
        print("ConnectionSolver: started.")
        self.results_producer.start()
        self.query_consumer.start()

    def stop(self):
        self.query_consumer.stop()
        self.results_producer.stop()
        self.connection_solver.data_manager.stop()

    def consume_query(self, query: ConnectionQuery):
        connection_results = self.connection_solver.find_connections(query)
        self.results_producer.send_msg(connection_results)


if __name__ == "__main__":
    start_connection_solver()
