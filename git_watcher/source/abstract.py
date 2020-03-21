import asyncio
import heapq
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from urllib.parse import urljoin

from aiohttp import ClientSession, ClientResponseError

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


class AbstractProvider(ABC):
    base_url: str
    contributors: List[Contributor] = []
    throttler: Throttler
    attempts_count: int = 10
    attempts_max_interval: int = 10

    def __init__(self, config):
        self.config = config
        self.owner = config.dest.owner
        self.repo = config.dest.repo

    @property
    @abstractmethod
    def path_commits(self):
        pass

    @abstractmethod
    def parse_contributors(self, res: Dict[str, Any]):
        pass

    async def update_contributors(self):
        url = urljoin(self.base_url, self.path_commits)
        res = await self.request('GET', url)
        self.contributors = list(self.parse_contributors(res))

    async def request(self, method, url, *a, **kw):
        for _ in range(self.attempts_count):
            try:
                async with self.throttler, self.session() as s, \
                        s.request(method, url, *a, **kw, raise_for_status=True) as resp:
                    return await resp.json()
            except ClientResponseError as ex:
                logging.warning(f'Error: {ex}')
                await asyncio.sleep(self.attempts_max_interval)
        raise RuntimeError(f"give up after {self.attempts_count} attempts on {url}")

    def new_contributor(self, d):
        return Contributor(name=d['name'], email=d['email'], count=1)

    def get_contributors(self, size=30):
        return heapq.nlargest(size, self.contributors, key=lambda a: a.count)

    @staticmethod
    def session(*args, **kwargs):
        return ClientSession(*args, **kwargs)
