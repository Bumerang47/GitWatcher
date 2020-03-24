import asyncio
import logging

from git_watcher import logger
from git_watcher.config import base_parser
from git_watcher.watcher import Watcher

config = base_parser()

if not config.debug:
    logger.propagate = False

try:
    watcher = Watcher(config)
    asyncio.run(watcher.run())
except KeyboardInterrupt:
    exit()
finally:
    logging.shutdown()
