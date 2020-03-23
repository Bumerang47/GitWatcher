import asyncio
import heapq
import logging
import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator, Generator, Mapping

from aiohttp import ClientSession, ClientResponseError, ClientResponse

from .. import logger
from ..objects import Contributor


class Throttler:

    def __init__(self, interval=6.0):
        self.interval = interval
        self.last_event_time = None
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        async with self.lock:
            now = time.monotonic()
            delay = 0
            if self.last_event_time is not None:
                delay = max(0, self.last_event_time + self.interval - now)
                if delay:
                    await asyncio.sleep(delay)
            self.last_event_time = now + delay

    async def __aexit__(self, *exc_info):
        pass


class Request:

    def __init__(self, method, url, *args, **kwargs):
        self.method = method
        self.url = url
        self.args = args
        self.kwargs = kwargs
        self.paginate = {}

    def __repr__(self):
        return f"Request({self.method}, {self.url}, *{self.args}, **{self.kwargs})"


RequestsGenerator = Generator[Request, None, None]


class AbstractProvider(ABC):
    base_url: str
    contributors: Dict[str, Contributor]
    throttler: Throttler

    since: Optional[datetime]
    until: Optional[datetime]
    branch: Optional[str]

    attempts_count: int = 10
    attempts_max_interval: int = 60
    limit_exceeded: bool = False

    def __init__(self, config):
        self.config = config
        self.owner = config.dest.owner
        self.repo = config.dest.repo

        self.since = config.since
        self.until = config.until
        self.branch = config.branch
        self.contributors = {}

    @abstractmethod
    def parse_contributors(self, res: Dict[str, Any]):
        """ Return contributors instance from raw response of commits
        """

    @abstractmethod
    async def update_contributors(self):
        """ Request and load new contributors from git repository

        """

    @abstractmethod
    def generate_requests(self, *args, **kwargs) -> RequestsGenerator:
        """
        Generate sequence of args and kwargs for aiohttp client session request
        """

    async def request(self, *args, **kwargs) -> AsyncGenerator:
        """
        Generate and call each possible request for results
        """

    @asynccontextmanager
    async def single_request(self, req: Request) -> AsyncGenerator[ClientResponse, None]:
        """
        Main safely request for one result
        """

        for _ in range(self.attempts_count):
            try:
                async with self.throttler, self.session() as s, \
                        s.request(req.method, req.url, *req.args, **req.kwargs,
                                  raise_for_status=True) as resp:
                    yield resp
            except ClientResponseError as ex:
                headers: Mapping = ex.headers or {}
                remain = headers.get('X-RateLimit-Remaining')
                if remain == '0':
                    self.limit_exceeded = True
                    rate_reset = int(headers.get('X-RateLimit-Reset', 0))
                    now_t_stamp = datetime.utcnow().timestamp()
                    wait_reset = int(rate_reset - now_t_stamp)

                    logger.warning(f'API rate limit exceeded, wait {wait_reset}s')
                    await asyncio.sleep(wait_reset)
                    continue

                logging.warning(f'Error: {ex}')
                await asyncio.sleep(self.attempts_max_interval)
            else:
                self.limit_exceeded = False
                return
        raise RuntimeError(f'give up after {self.attempts_count} attempts on {req.url}')

    def get_contributors(self, size=30):
        return heapq.nlargest(size, self.contributors.values(), key=lambda a: a.count)

    @staticmethod
    def session(*args, **kwargs):
        return ClientSession(*args, **kwargs)
