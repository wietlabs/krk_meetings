import json
from flask import Flask, request, Response, jsonify
from multiprocessing import Value

from src.config import EXCHANGES
from src.rabbitmq.RmqConsumer import RmqOneMsgConsumer
from src.rabbitmq.RmqProducer import RmqProducer


def start_flask_server():
    flask_server = FlaskServer("FlaskServer")
    flask_server.start()


class FlaskServer:
    app = None

    def __init__(self, name):
        self.app = Flask(name)
        self.task_id = Value('i', 0)
        self.connection_producer = RmqProducer(EXCHANGES.CONNECTION_QUERY.value)
        self.meeting_producer = RmqProducer(EXCHANGES.MEETING_QUERY.value)
        self.sequence_producer = RmqProducer(EXCHANGES.SEQUENCE_QUERY.value)

    def run(self):
        self.app.run(threaded=True, port=5000)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)

    def start(self):
        self.add_endpoint("/connection", "connection", self.handle_connection, ["POST"])
        self.add_endpoint("/meeting", "meeting", self.handle_meeting, ["POST"])
        self.add_endpoint("/sequence", "sequence", self.handle_sequence, ["POST"])
        print("FlaskServer: started")
        self.run()

    def handle_connection(self):
        return self.handle_query_post(EXCHANGES.CONNECTION_RESULTS.value, self.connection_producer)

    def handle_meeting(self):
        return self.handle_query_post(EXCHANGES.MEETING_RESULTS.value, self.meeting_producer)

    def handle_sequence(self):
        return self.handle_query_post(EXCHANGES.SEQUENCE_RESULTS.value, self.sequence_producer)

    def handle_query_post(self, exchange, producer):
        print(exchange)
        request_json = json.loads(request.get_json())
        with self.task_id.get_lock():
            self.task_id.value += 1
            task_id = self.task_id.value
        request_json["query_id"] = task_id
        producer.send_msg(request_json)
        connection_consumer = RmqOneMsgConsumer(exchange, task_id)
        result = connection_consumer.receive_msg()
        return jsonify(result), 202

