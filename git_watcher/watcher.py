import asyncio
from typing import List, Any

from .display import Throbber, Table, clear
from .objects import Contributor
from .source import GitHub


class Watcher:
    throbber: Throbber
    contributors: List[Any] = []
    update_interval = 20

    def __init__(self, config):
        self.provider = GitHub(config)
        self.config = config
        self.throbber = Throbber()

    async def update(self):
        while True:
            await self.provider.update_contributors()
            self.contributors = self.provider.get_contributors()
            await asyncio.sleep(self.update_interval)

    async def display(self):
        while True:
            await asyncio.sleep(0.3)
            clear()

            table = Table(Contributor, self.contributors)
            print(table, self.throbber, sep='\n')

    async def run(self):
        await asyncio.gather(
            self.update(),
            self.display(),
        )
