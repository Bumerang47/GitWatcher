import argparse
from datetime import datetime
from numbers import Number

from .objects import Destination


def parse_date(v):
    if not v or isinstance(v, datetime):
        return v
    elif isinstance(Number, v):
        return datetime.fromtimestamp(v)
    else:
        return datetime.fromisoformat(v)


def base_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('dest', type=Destination.from_str, metavar='url', help='Repository URL')
    parser.add_argument('--branch', type=str, default='master', required=False,
                        help='Branch name for analyze commits')
    parser.add_argument('--since', type=parse_date, default=None, required=False,
                        help='Get result after this date. This is a timestamp or ISO format')
    parser.add_argument('--until', type=parse_date, default=None,
                        help='Get result before this date. This is a timestamp or ISO format')
    return parser.parse_args()
