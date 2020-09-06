from src.rabbitmq.RmqProducer import RmqProducer

if __name__=="__main__":
    writer = RmqProducer("example")
    writer.send_msg("message")
    writer.send_msg("message")
    writer.send_msg("message")
    writer.send_msg("message")
    writer.send_msg("message")
