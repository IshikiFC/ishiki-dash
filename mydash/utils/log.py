import logging

LOG_DATE_FORMAT = "%Y-%m-%d %I:%M:%S"
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'


def init_logger(debug=False):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        datefmt=LOG_DATE_FORMAT, format=LOG_FORMAT)