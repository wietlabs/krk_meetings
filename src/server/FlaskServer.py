import json
from flask import Flask, request, Response, jsonify
from multiprocessing import Value

from src.exchanges import EXCHANGES
from src.rabbitmq.RmqConsumer import RmqOneMsgConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.data_provider.FloydDataProvider import FloydDataProvider
from src.config import SolverStatusCodes


def start_flask_server():
    flask_server = FlaskServer('FlaskServer')
    flask_server.start()


class FlaskServer:
    app = None

    def __init__(self, name):
        self.app = Flask(name)
        self.app.config['JSON_AS_ASCII'] = False
        self.task_id = Value('i', 0)
        self.connection_producer = RmqProducer(EXCHANGES.CONNECTION_QUERY.value)
        self.meeting_producer = RmqProducer(EXCHANGES.MEETING_QUERY.value)
        self.sequence_producer = RmqProducer(EXCHANGES.SEQUENCE_QUERY.value)
        # TODO auto+update
        floyd_data = FloydDataProvider.load_floyd_data()
        self.routes_df = floyd_data.routes_df
        self.stops_df_by_name = floyd_data.stops_df_by_name
        self.stops_df = floyd_data.stops_df
        self.routes_to_stops_dict = floyd_data.routes_to_stops_dict

    def run(self):
        self.app.run(threaded=True, port=5000)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)

    def start(self):
        self.add_endpoint('/connection', 'connection', self.handle_connection, ['POST'])
        self.add_endpoint('/meeting', 'meeting', self.handle_meeting, ['POST'])
        self.add_endpoint('/sequence', 'sequence', self.handle_sequence, ['POST'])
        print('FlaskServer: started')
        self.run()

    def handle_connection(self):
        request_json = json.loads(request.get_json())
        result = self.handle_query_post(EXCHANGES.CONNECTION_RESULTS.value, self.connection_producer, request_json)
        if result in [SolverStatusCodes.BAD_END_STOP_NAME.value, SolverStatusCodes.BAD_START_STOP_NAME.value]:
            return jsonify(result), 400
        return jsonify(result), 202

    def handle_meeting(self):
        try:
            request_json = json.loads(request.get_json())
            result = self.handle_query_post(EXCHANGES.MEETING_RESULTS.value, self.meeting_producer, request_json)
            return jsonify(result), 202
        except Exception as e:
            return jsonify(e), 400

    def handle_sequence(self):
        try:
            request_json = json.loads(request.get_json())
            result = self.handle_query_post(EXCHANGES.SEQUENCE_RESULTS.value, self.sequence_producer, request_json)
            return jsonify(result), 202
        except Exception as e:
            return jsonify(e), 400

    def handle_query_post(self, exchange, producer, request_json):
        with self.task_id.get_lock():
            self.task_id.value += 1
            task_id = self.task_id.value
        request_json['query_id'] = task_id
        producer.send_msg(request_json)
        connection_consumer = RmqOneMsgConsumer(exchange, task_id)
        result = connection_consumer.receive_msg()
        return result


if __name__ == '__main__':
    start_flask_server()
