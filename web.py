import logging
import os
from typing import Optional

from flask import Flask, send_from_directory

from blueprints.admin import admin_blueprint
from blueprints.sync import sync_blueprint

logger = logging.getLogger(__name__)

app = Flask(__name__)


def strtobool(value: Optional[str]) -> bool:
    if value is None:
        return False
    value = value.lower()
    if value in ("y", "yes", "on", "1", "true", "t"):
        return True
    return False


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


if strtobool(os.environ.get('ADMIN_MODE')):
    app.register_blueprint(admin_blueprint, url_prefix='/')
else:
    app.register_blueprint(sync_blueprint, url_prefix='/')
