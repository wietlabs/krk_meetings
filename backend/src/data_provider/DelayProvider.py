import time
from src.data_provider.Downloader import Downloader
from src.rabbitmq.RmqProducer import RmqProducer
from src.exchanges import EXCHANGES, MESSAGES
from src.config import FloydDataPaths
from src.utils import save_pickle


def start_delays_provider():
    delays_provider = DelaysProvider()
    delays_provider.start()


class DelaysProvider:
    def __init__(self):
        self.floyd_data_producer = RmqProducer(EXCHANGES.DELAYS_PROVIDER.value)
        self.downloader = Downloader()

    def start(self):
        print("DelaysProvider: has started.")
        while True:
            delays_df = self.get_delays_df()
            delays = self.extract_delays(delays_df)
            save_pickle(delays, FloydDataPaths.delays_dict.value)
            self.floyd_data_producer.send_msg(MESSAGES.DELAYS_UPDATED.value, lost_stream_msg="Solvers are down.")
            print("Delays_provider: delays updated")
            time.sleep(120)

    def extract_delays(self, delays_df):
        return None

    def get_delays_df(self):
        return None
