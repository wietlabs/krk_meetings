from threading import Thread
from flask import Flask, request, Response, jsonify
from multiprocessing import Value

from src.data_managers.FlaskDataManager import FlaskDataManager
from src.exchanges import EXCHANGES
from src.rabbitmq.RmqConsumer import RmqConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.server.CacheDict import CacheDict
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.config import ErrorCodes
from src.data_classes.MeetingQuery import MeetingQuery
from src.data_classes.SequenceQuery import SequenceQuery


def start_flask_server():
    flask_server = FlaskServer('FlaskServer')
    flask_server.start()


class FlaskServer:
    app = None

    def __init__(self, name):
        self.app = Flask(name)
        self.app.config['JSON_AS_ASCII'] = False
        self.query_id = Value('i', 0)
        self.cache = CacheDict(cache_len=1000)

        self.connection_producer = RmqProducer(EXCHANGES.CONNECTION_QUERY.value)
        self.meeting_producer = RmqProducer(EXCHANGES.MEETING_QUERY.value)
        self.sequence_producer = RmqProducer(EXCHANGES.SEQUENCE_QUERY.value)

        self.connection_consumer = RmqConsumer(EXCHANGES.FLASK_SERVER_CONNECTION.value, self.consume_rabbit_results)
        self.meeting_consumer = RmqConsumer(EXCHANGES.FLASK_SERVER_MEETING.value, self.consume_rabbit_results)
        self.sequence_consumer = RmqConsumer(EXCHANGES.FLASK_SERVER_SEQUENCE.value, self.consume_rabbit_results)

        self.connection_consumer_thread = Thread(target=self.connection_consumer.start, args=[])
        self.meeting_consumer_thread = Thread(target=self.meeting_consumer.start, args=[])
        self.sequence_consumer_thread = Thread(target=self.sequence_consumer.start, args=[])

        self.data_manager = FlaskDataManager()
        self.stops = None

    def update_data(self):
        if not self.data_manager.up_to_date:
            data = self.data_manager.get_updated_data()
            self.stops = data['stops']

    def run(self):
        self.app.run(threaded=True, host='0.0.0.0', port=5000)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)

    def start(self):
        self.data_manager.start()
        self.data_manager.update_data()
        self.update_data()

        self.connection_producer.start()
        self.meeting_producer.start()
        self.sequence_producer.start()
        self.connection_consumer_thread.start()
        self.meeting_consumer_thread.start()
        self.sequence_consumer_thread.start()

        self.add_endpoint('/connection', 'connection', self.handle_post_connection, ['POST'])
        self.add_endpoint('/meeting', 'meeting', self.handle_post_meeting, ['POST'])
        self.add_endpoint('/sequence', 'sequence', self.handle_post_sequence, ['POST'])
        self.add_endpoint('/result/<query_id>', 'results', self.handle_get_query, ['GET'])
        self.add_endpoint(f'/stops', 'stops', self.handle_get_stops, ['GET'])

        print('FlaskServer: started')
        self.run()

    def consume_rabbit_results(self, result):
        result["result"]["is_done"] = True
        self.cache[result["query_id"]] = {"result": result["result"], "error": result["error"]}

    def handle_get_query(self, query_id):
        try:
            query_id = int(query_id)
        except ValueError:
            return jsonify(ErrorCodes.BAD_QUERY_ID_TYPE.value), 400
        try:
            result = self.cache[query_id]
        except KeyError:
            return jsonify(ErrorCodes.BAD_QUERY_ID_VALUE.value), 400

        if result["result"]["is_done"] and result["error"] != ErrorCodes.OK.value:
            return jsonify(result["error"]), 400
        return jsonify(result["result"]), 202

    def handle_get_stops(self):
        return jsonify(self.stops), 202

    def handle_post_connection(self):
        request_json = request.get_json()
        result = self.handle_query_post(self.connection_producer, request_json, ConnectionQuery,
                                        ErrorCodes.BAD_CONNECTION_JSON_FORMAT.value)
        return result

    def handle_post_meeting(self):
        request_json = request.get_json()
        result = self.handle_query_post(self.meeting_producer, request_json, MeetingQuery,
                                        ErrorCodes.BAD_MEETING_JSON_FORMAT.value)
        return result

    def handle_post_sequence(self):
        request_json = request.get_json()
        result = self.handle_query_post(self.sequence_producer, request_json, SequenceQuery,
                                        ErrorCodes.BAD_SEQUENCE_JSON_FORMAT.value)
        return result

    def handle_query_post(self, producer, request_json, query_class, parsing_error_message):
        try:
            query_class.from_dict(request_json)
        except TypeError:
            return jsonify(parsing_error_message), 400
        with self.query_id.get_lock():
            self.query_id.value += 1
            query_id = self.query_id.value
        request_json["query_id"] = query_id
        producer.send_msg(request_json)
        self.cache[query_id] = {"result": {"is_done": False}}
        return jsonify({"query_id": query_id}), 202


if __name__ == '__main__':
    start_flask_server()
