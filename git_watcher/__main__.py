import asyncio
import logging

from git_watcher import config
from git_watcher.watcher import Watcher

try:
    watcher = Watcher(config)
    asyncio.run(watcher.run())
except KeyboardInterrupt:
    exit()
finally:
    logging.shutdown()
