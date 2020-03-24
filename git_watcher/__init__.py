import logging
from logging import config as log_conf

import pkg_resources

resource_package = __name__
path_conf = pkg_resources.resource_filename(__name__, 'logging.conf')
log_conf.fileConfig(path_conf, disable_existing_loggers=False)
logger = logging.getLogger(__name__)
