import asyncio
import logging

from git_watcher.watcher import Watcher
from . import logger
from .config import base_parser

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
