import argparse
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, Mock

import pytest
from aiohttp import ClientResponseError
from aiohttp import RequestInfo

from git_watcher import logger
from git_watcher.objects import Destination
from git_watcher.source import GitHub

logger.disabled = True


@pytest.fixture(scope='module')
def _config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', type=Destination.from_str, metavar='url',
                        default='https://github.com/TestAuthor/testProject')
    parser.add_argument('--branch', type=str, default='master', required=False)
    parser.add_argument('--since', type=datetime, default=None, required=False)
    parser.add_argument('--until', type=datetime, default=None)
    parser.add_argument('--no-debug', default=True, dest='debug', action='store_false')
    parser.add_argument('--auth', default='', type=str)
    parser.add_argument('--update-interval', default=600, type=int)
    parser.add_argument('--size-top-table', default=30, type=int)

    parser.set_defaults(url='https://github.com/TestAuthor/testProject')
    args, _ = parser.parse_known_args()

    with patch('git_watcher.config.base_parser') as conf:
        conf.return_value = args
        yield args


@pytest.fixture()
async def github(_config):
    github = GitHub(_config)
    yield github


@pytest.fixture(scope="session")
def _fixture_contrib_data():
    p = Path(__file__).with_name("fixtures") / "github_response.json"
    if p.exists():
        yield json.loads(p.read_text())


@pytest.fixture()
def patch_request_contrib(_fixture_contrib_data):
    with patch('git_watcher.source.github.GitHub.single_request') as mk:
        mk.return_value.__aenter__.return_value.headers = {}
        mk.return_value.__aenter__.return_value.json.return_value = _fixture_contrib_data
        yield


@pytest.fixture()
def patch_session_request():
    with patch('git_watcher.source.abstract.ClientSession.request') as rq:
        yield rq


class UnstableRequester:
    """ For multiple requests context in the patch side effect
    with unsuccess requests and unsuccessful after

    """

    def __init__(self, raise_fails=1, return_value=None):
        self.raise_fails = raise_fails
        self.count_raise = 0
        self.return_value = return_value

    async def __aenter__(self):
        if self.raise_fails > self.count_raise:
            self.count_raise += 1
            raise ClientResponseError(RequestInfo('', '', Mock(), ''), ())
        return self.return_value or {}

    async def __aexit__(self, exc_type, exc, tb):
        return self.return_value or {}
