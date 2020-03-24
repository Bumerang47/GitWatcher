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
    parser = argparse.ArgumentParser(prog='git_wathcer',
                                     description='Simple dashboard of git repository')
    parser.add_argument('dest', type=Destination.from_str, metavar='URL', help='Repository URL')
    parser.add_argument('--branch', type=str, default='master', required=False,
                        help='branch name for analyze commits [%(default)s].')
    parser.add_argument('--since', type=parse_date, default=None, required=False,
                        help='get result after this date. This is a timestamp or ISO format '
                             '[%(default)s]')
    parser.add_argument('--until', type=parse_date, default=None,
                        help='get result before this date. This is a timestamp or ISO format '
                             '[%(default)s]')
    parser.add_argument('--no-debug', default=True, dest='debug', action='store_false',
                        help='disable debug and output to stdout [%(default)s].')
    parser.add_argument('--auth', default='', type=str,
                        help='authenticate for pass or just get more rate limit.\n'
                             'Example: `<login>:<pass>` or `<clent_id>:<clent_secret>`')
    parser.add_argument('--update-interval', default=600, type=int,
                        help='period in second between repeat upload data [%(default)s].')
    parser.add_argument('--size-top-table', default=30, type=int,
                        help='size table of top contributors [%(default)s].')
    args, _ = parser.parse_known_args()
    return args
