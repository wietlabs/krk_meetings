import logging
from logging import handlers
import sys


def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")

    fh = handlers.RotatingFileHandler("krk_meet_log.txt", maxBytes=(1048576 * 5), backupCount=7)
    fh.setFormatter(format)
    log.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    return log
