from src.rabbitmq.RmqConsumer import RmqConsumer

if __name__=="__main__":
    reader = RmqConsumer("example", lambda x: print(x))
    reader.start()
