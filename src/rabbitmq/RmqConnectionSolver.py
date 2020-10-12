from src.config import EXCHANGES
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.solver.ConnectionSolver import ConnectionSolver
from src.solver.DataManager import DataManager


def start_connection_solver():
    meeting_solver = RmqConnectionSolver()
    meeting_solver.start()


class RmqConnectionSolver:
    def __init__(self):
        self.connection_solver = ConnectionSolver()
        self.query_consumer = RmqConsumer(EXCHANGES.CONNECTION_QUERY.value, self.consume_connection_query)
        self.results_producer = RmqProducer(EXCHANGES.CONNECTION_RESULTS.value)

    def start(self):
        print("ConnectionSolver: started.")
        self.query_consumer.start()

    def stop(self):
        self.query_consumer.stop()
        self.results_producer.stop()
        self.connection_solver.data_manager.stop()

    def consume_connection_query(self, query: ConnectionQuery):
        print("consume_connection_query")
        connections = self.connection_solver.find_connections(query)
        self.results_producer.send_msg(connections, query.query_id)
        print("results_sent")
