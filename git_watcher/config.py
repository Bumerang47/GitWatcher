import argparse
from datetime import datetime, timezone as tz
from numbers import Number

from .objects import Destination


def parse_date(v):
    if not v or isinstance(v, datetime):
        return v
    elif isinstance(v, Number):
        return datetime.fromtimestamp(v).replace(microsecond=0, tzinfo=tz.utc)
    else:
        return datetime.fromisoformat(v).replace(microsecond=0, tzinfo=tz.utc)


def base_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('dest', type=Destination.from_str, metavar='url', help='Repository URL')
    parser.add_argument('--branch', type=str, default='master', required=False,
                        help='Branch name for analyze commits')
    parser.add_argument('--since', type=parse_date, default=None, required=False,
                        help='Get result after this date. This is a timestamp or ISO format')
    parser.add_argument('--until', type=parse_date, default=None,
                        help='Get result before this date. This is a timestamp or ISO format')
    parser.add_argument('--no-debug', default=True, dest='debug', action='store_false',
                        help='Disable debug and output to stdout')
    return parser.parse_args()
