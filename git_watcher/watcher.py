import asyncio
from collections import Counter
from typing import List, Any, Dict

from . import logger
from .display import Throbber, Table, clear_output
from .objects import Contributor
from .source import GitHub


class Watcher:
    throbber: Throbber
    contributors: List[Any]
    pull_info: Dict

    def __init__(self, config):
        self.provider = GitHub(config)
        self.config = config
        self.throbber = Throbber()

        self.contributors = []
        self.pull_info = Counter(closed=0, opened=0, old_opened=0)
        self.first_boot = True

    async def update(self):
        while True:
            await self.provider.update_pulls_info()
            self.pull_info = self.provider.pulls_info

            await self.provider.update_contributors()
            self.contributors = self.provider.get_contributors()

            self.first_boot = False
            await asyncio.sleep(self.config.update_interval)

    async def display(self):
        while True:
            await asyncio.sleep(0.3)
            clear_output()

            info_status = 'Ø' if self.provider.limit_exceeded else ''
            table = Table(Contributor, self.contributors)
            pulls_text = (
                '\nPR opened - {opened}\n'
                'PR old opened - {old_opened}\n'
                'PR closed - {closed}'
            ).format_map(self.pull_info)

            status = self.first_boot and 'Loading ...' or ' '
            logger.info(f'{pulls_text}\n\n'
                        f'Top contributors:\n'
                        f'{table}\n'
                        f'''{self.throbber} | {status}'''
                        f'{info_status}')

    async def run(self):
        await asyncio.gather(
            self.update(),
            self.display(),
        )
