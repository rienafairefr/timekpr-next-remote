import logging

import os
import sys

from web import app
from sync import sync

logger = logging.getLogger(__name__)
if __name__ == "__main__":
    logging_level = getattr(logging, os.environ.get('LOGGER_LEVEL', 'INFO'))
    logging.basicConfig(level=logging_level)
    logger.info(logging.getLogger("paramiko"))
    logging.getLogger("paramiko").propagate = False
    if sys.argv[1] == 'web':
        app.run(host="0.0.0.0", port=8080)
    elif sys.argv[1] == 'sync':
        sync()
