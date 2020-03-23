import asyncio
from typing import List

from . import logger
from .display import Throbber, Table, clear_output
from .objects import Contributor, Statistic
from .source import GitHub


class Watcher:
    throbber: Throbber
    contributors: List[Contributor]
    statistic: List[Statistic]

    def __init__(self, config):
        self.provider = GitHub(config)
        self.config = config
        self.throbber = Throbber()

        self.contributors = [Contributor('-')]
        self.statistic = [self.provider.pulls_info,
                          self.provider.issues_info]
        self.first_boot = True

    async def update(self):
        while True:
            await self.provider.update_pulls_info()
            await self.provider.update_issues_info()
            await self.provider.update_contributors()

            self.contributors = self.provider.get_top_contributors()

            self.first_boot = False
            await asyncio.sleep(self.config.update_interval)

    async def display(self):
        while True:
            await asyncio.sleep(0.3)
            clear_output()

            info_status = 'Ø' if self.provider.limit_exceeded else ''
            table_statistic = Table(Statistic, self.statistic)
            table = Table(Contributor, self.contributors)

            status = self.first_boot and 'Loading ...' or ' '
            logger.info(f'Statistic Info:\n'
                        f'{table_statistic}\n\n'
                        f'Top contributors:\n'
                        f'{table}\n\n'
                        f'''{self.throbber} | {status}'''
                        f'{info_status}')

    async def run(self):
        await asyncio.gather(
            self.update(),
            self.display(),
        )
