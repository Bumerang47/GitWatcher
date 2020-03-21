import logging
from logging import config as log_conf

from .config import base_parser

log_conf.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

config = base_parser()

if not config.debug:
    logger.propagate = 0
