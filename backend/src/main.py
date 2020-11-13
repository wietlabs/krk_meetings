from src.exchanges import EXCHANGES
from src.rabbitmq.RmqProducer import RmqProducer


class MsgSender:
    def __init__(self):
        self.floyd_data_producer = RmqProducer(EXCHANGES.DELAYS_PROVIDER.value)

    def send_message(self):
        self.floyd_data_producer.send_msg("DATA UPDATED", lost_stream_msg="Solvers are down.")


if __name__ == "__main__":
    sender = MsgSender()
    sender.send_message()
