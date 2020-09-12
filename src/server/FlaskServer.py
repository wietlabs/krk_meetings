import json
from flask import Flask, request, Response, jsonify
from multiprocessing import Value

from src.config import EXCHANGES
from src.rabbitmq.RmqConsumer import RmqOneMsgConsumer
from src.rabbitmq.RmqProducer import RmqProducer
from src.data_provider.FloydDataProvider import FloydDataProvider


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
        self.add_endpoint("/connection", "connection", self.handle_connection, ["POST"])
        self.add_endpoint("/meeting", "meeting", self.handle_meeting, ["POST"])
        self.add_endpoint("/sequence", "sequence", self.handle_sequence, ["POST"])
        print("FlaskServer: started")
        self.run()

    def handle_connection(self):
        request_json = json.loads(request.get_json())
        request_json = {
            "start_date": request_json["start_date"],
            "start_time": request_json["start_time"],
            "start_stop_id": int(self.stops_df_by_name.at[request_json["start_stop_name"], 'stop_id']),
            "end_stop_id": int(self.stops_df_by_name.at[request_json["end_stop_name"], 'stop_id'])
        }
        connection_results = self.handle_query_post(EXCHANGES.CONNECTION_RESULTS.value, self.connection_producer,
                                                    request_json)
        connection_results = list(map(lambda transfers:
                                      {
                                          "transfers": list(map(lambda t:
                                                                {
                                                                    "start_date": t["start_date"],
                                                                    "start_time": t["start_time"],
                                                                    "end_date": t["end_date"],
                                                                    "end_time": t["end_time"],
                                                                    "stops": self.get_stop_list(
                                                                        t["route_id"], t["start_stop_id"],
                                                                        t["end_stop_id"])
                                                                }
                                                                , transfers))
                                      }, connection_results))
        connection_results = {"connections": connection_results}
        return jsonify(connection_results), 202

    def handle_meeting(self):
        request_json = json.loads(request.get_json())
        result = self.handle_query_post(EXCHANGES.MEETING_RESULTS.value, self.meeting_producer, request_json)
        return jsonify(result), 202

    def handle_sequence(self):
        request_json = json.loads(request.get_json())
        result = self.handle_query_post(EXCHANGES.SEQUENCE_RESULTS.value, self.sequence_producer, request_json)
        return jsonify(result), 202

    def handle_query_post(self, exchange, producer, request_json):
        with self.task_id.get_lock():
            self.task_id.value += 1
            task_id = self.task_id.value
        request_json["query_id"] = task_id
        producer.send_msg(request_json)
        connection_consumer = RmqOneMsgConsumer(exchange, task_id)
        result = connection_consumer.receive_msg()
        return result

    def get_stop_list(self, route_id, start_stop_id, end_stop_id):
        stop_ids_list = self.routes_to_stops_dict[route_id]
        stops = []
        for stop_id in stop_ids_list:
            if stop_id == start_stop_id:
                stops = [start_stop_id]
            elif stops:
                stops.append(stop_id)
                if stop_id == end_stop_id:
                    break
        stops = list(map(lambda s:
                         {
                             "name": self.stops_df.at[s, 'stop_name'],
                             "latitude": self.stops_df.at[s, 'stop_lat'],
                             "longitude": self.stops_df.at[s, 'stop_lon'],
                         }, stops))
        return stops
