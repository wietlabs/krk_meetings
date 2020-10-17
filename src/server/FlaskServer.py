import json
from threading import Thread

from flask import Flask, request, Response, jsonify
from multiprocessing import Value

from src.exchanges import EXCHANGES
from src.rabbitmq.RmqConsumer import RmqOneMsgConsumer, RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.data_provider.FloydDataProvider import FloydDataProvider
from src.config import SolverStatusCodes
from src.server.CacheDict import CacheDict


def start_flask_server():
    flask_server = FlaskServer('FlaskServer')
    flask_server.start()


class FlaskServer:
    app = None

    def __init__(self, name):
        self.app = Flask(name)
        self.app.config['JSON_AS_ASCII'] = False
        self.query_id = Value('i', 0)
        self.connection_producer = RmqProducer(EXCHANGES.CONNECTION_QUERY.value)
        self.meeting_producer = RmqProducer(EXCHANGES.MEETING_QUERY.value)
        self.sequence_producer = RmqProducer(EXCHANGES.SEQUENCE_QUERY.value)
        self.cache = CacheDict(cache_len=1000)

        self.connection_consumer = RmqConsumer(EXCHANGES.FLASK_SERVER_CONNECTION.value, self.consume_rabbit_results)
        self.connection_consumer_thread = Thread(target=self.connection_consumer.start, args=[])
        self.connection_consumer_thread.start()

        self.meeting_consumer = RmqConsumer(EXCHANGES.FLASK_SERVER_MEETING.value, self.consume_rabbit_results)
        self.meeting_consumer_thread = Thread(target=self.meeting_consumer.start, args=[])
        self.meeting_consumer_thread.start()

        self.sequence_consumer = RmqConsumer(EXCHANGES.FLASK_SERVER_SEQUENCE.value, self.consume_rabbit_results)
        self.sequence_consumer_thread = Thread(target=self.sequence_consumer.start, args=[])
        self.sequence_consumer_thread.start()

    def run(self):
        self.app.run(threaded=True, port=5000)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)

    def start(self):
        self.add_endpoint('/connection', 'connection', self.handle_connection, ['POST'])
        self.add_endpoint('/meeting', 'meeting', self.handle_meeting, ['POST'])
        self.add_endpoint('/sequence', 'sequence', self.handle_sequence, ['POST'])
        self.add_endpoint('/result/<query_id>', 'results', self.handle_get, ['GET'])
        print('FlaskServer: started')
        self.run()

    def consume_rabbit_results(self, result):
        self.cache[result["query_id"]] = result["result"]

    def handle_get(self, query_id):
        query_id = int(query_id)
        result = self.cache[query_id]
        if result in [SolverStatusCodes.BAD_END_STOP_NAME.value, SolverStatusCodes.BAD_START_STOP_NAME.value]:
            return jsonify(result), 400
        return jsonify(result), 202

    def handle_connection(self):
        request_json = json.loads(request.get_json())
        result = self.handle_query_post(self.connection_producer, request_json)
        return jsonify(result), 202

    def handle_meeting(self):
        request_json = json.loads(request.get_json())
        result = self.handle_query_post(self.meeting_producer, request_json)
        return jsonify(result), 202

    def handle_sequence(self):
        request_json = json.loads(request.get_json())
        result = self.handle_query_post(self.sequence_producer, request_json)
        return jsonify(result), 202

    def handle_query_post(self, producer, request_json):
        with self.query_id.get_lock():
            self.query_id.value += 1
            query_id = self.query_id.value
        request_json['query_id'] = query_id
        producer.send_msg(request_json)
        self.cache[query_id] = "Results not ready yet."
        return query_id


if __name__ == '__main__':
    start_flask_server()
