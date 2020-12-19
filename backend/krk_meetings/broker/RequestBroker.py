from threading import Thread
from flask import Flask, request, Response, jsonify
from multiprocessing import Value

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from krk_meetings.data_managers.FlaskDataManager import FlaskDataManager
from krk_meetings.exchanges import EXCHANGES
from krk_meetings.rabbitmq.RmqConsumer import RmqConsumer
from krk_meetings.rabbitmq.RmqProducer import RmqProducer
from krk_meetings.broker.CacheDict import CacheDict
from krk_meetings.data_classes.ConnectionQuery import ConnectionQuery
from krk_meetings.config import ErrorCodes
from krk_meetings.data_classes.MeetingQuery import MeetingQuery
from krk_meetings.data_classes.SequenceQuery import SequenceQuery
from krk_meetings.logger import get_logger

logger = get_logger(__name__)


def start_flask_server():
    flask_server = RequestBroker('SolverBroker')
    flask_server.start()


class RequestBroker:
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
        self.last_update_date = None
        self.limiter = Limiter(self.app, key_func=get_remote_address, default_limits=["100 per hour"])
        self.limiter.exempt(self.handle_get_query)
        self.limiter.exempt(self.handle_get_stops)

    def update_data(self):
        data = self.data_manager.get_updated_data()
        self.stops = data['stops']
        self.last_update_date = self.data_manager.last_data_update

    def run(self):
        self.app.run(threaded=True, host='0.0.0.0', port=5000)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)

    def start(self):
        self.data_manager.start()
        if self.data_is_loaded():
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

        logger.info('SolverBroker: started')
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
            if result["error"] in [ErrorCodes.INTERNAL_SERVER_ERROR.value, ErrorCodes.INTERNAL_DATA_NOT_LOADED.value]:
                return jsonify(result["error"]), 500
            return jsonify(result["error"]), 400
        return jsonify(result["result"]), 202

    def handle_get_stops(self):
        if not self.data_is_loaded():
            return jsonify(ErrorCodes.INTERNAL_DATA_NOT_LOADED.value), 500
        if self.last_update_date < self.data_manager.last_data_update:
            self.update_data()
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
        if not query_class.validate(request_json):
            return jsonify(parsing_error_message), 400
        with self.query_id.get_lock():
            self.query_id.value += 1
            query_id = self.query_id.value
        request_json["query_id"] = query_id
        producer.send_msg(request_json)
        self.cache[query_id] = {"result": {"is_done": False}}
        return jsonify({"query_id": query_id}), 202

    def data_is_loaded(self):
        if self.data_manager.data_loaded:
            return True
        else:
            logger.warn(f"RequestBroker: Some pickles in data directory are missing this service won't "
                        f"work without them. Wait for DataProvider to finish processing GTFS files.")
            return False


if __name__ == '__main__':
    start_flask_server()
