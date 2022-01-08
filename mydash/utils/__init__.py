import logging
import urllib

LOG_DATE_FORMAT = "%Y-%m-%d %I:%M:%S"
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'


def init_logger(args):
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        datefmt=LOG_DATE_FORMAT, format=LOG_FORMAT)


def clean_name(s):
    return ''.join(s.strip().split())


def build_url(base_url, query_dict):
    query = urllib.parse.urlencode(query_dict)
    return f'{base_url}?{query}'