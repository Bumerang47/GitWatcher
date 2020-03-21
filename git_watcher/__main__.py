import asyncio

from git_watcher.config import base_parser
from git_watcher.watcher import Watcher

config = base_parser()
watcher = Watcher(config)
asyncio.run(watcher.run())
