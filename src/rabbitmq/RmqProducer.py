import pika


class RmqProducer:
    def __init__(self, exchange):
        self.exchange_name, self.exchange_type, self.routing_key, self.to_json, _ = exchange
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        if self.exchange_type:
            self.channel.exchange_declare(exchange=self.exchange_name,  exchange_type=self.exchange_type)
        else:
            self.channel.exchange_declare(exchange=self.exchange_name)

    def stop(self):
        self.connection.close()

    def send_msg(self, message, task_id=None):
        if task_id is None:
            routing_key = self.routing_key
        else:
            routing_key = self.routing_key + str(task_id)
        self.channel.basic_publish(exchange=self.exchange_name, routing_key=routing_key, body=self.to_json(message))
