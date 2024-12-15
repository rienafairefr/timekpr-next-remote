import logging

import os

from web import app

if __name__ == "__main__":
    logging_level = getattr(logging, os.environ.get('LOGGER_LEVEL', 'INFO'))
    logging.basicConfig(level=logging_level)
    logging.getLogger("paramiko").setLevel(logging_level)  # for example
    app.run(host="0.0.0.0", port=8080)
