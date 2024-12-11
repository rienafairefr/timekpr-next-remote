import logging

from flask import Flask, render_template, send_from_directory

import conf
import main
import os

app = Flask(__name__)
logger = logging.getLogger(__name__)

def validate_request(computer, user):
    if computer not in conf.trackme:
        return {"result": "fail", "message": "computer not in config"}
    if user not in conf.trackme[computer]:
        return {"result": "fail", "message": "user not in computer in config"}
    else:
        return {"result": "success", "message": "valid user and computer"}


@app.route("/config")
def config():
    return main.get_config()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_usage/<computer>/<user>")
def get_usage(computer, user):
    if validate_request(computer, user)["result"] == "fail":
        return validate_request(computer, user), 500
    ssh = main.get_connection(computer)
    usage = main.get_usage(user, computer, ssh)
    return {
        "result": usage["result"],
        "time_left": usage["time_left"],
        "time_spent": usage["time_spent"],
    }, 200


@app.route("/increase_time/<computer>/<user>/<seconds>")
def increase_time(computer, user, seconds):
    if validate_request(computer, user)["result"] == "fail":
        return validate_request(computer, user), 500
    ssh = main.get_connection(computer)
    if main.increase_time(seconds, ssh, user, computer):
        usage = main.get_usage(user, computer, ssh)
        return {
            "result": "success",
            "time_left": usage["time_left"],
            "time_spent": usage["time_spent"],
        }, 200
    else:
        return {"result": "fail"}, 500


@app.route("/decrease_time/<computer>/<user>/<seconds>")
def decrease_time(computer, user, seconds):
    if validate_request(computer, user)["result"] == "fail":
        return validate_request(computer, user), 500
    ssh = main.get_connection(computer)
    if main.decrease_time(seconds, ssh, user, computer):
        usage = main.get_usage(user, computer, ssh)
        return {
            "result": "success",
            "time_left": usage["time_left"],
            "time_spent": usage["time_spent"],
        }, 200
    else:
        return {"result": "fail"}, 500


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


if __name__ == "__main__":
    logging_level = getattr(logging, os.environ.get('LOGGER_LEVEL', 'INFO'))
    logging.basicConfig(level=logging_level)
    logging.getLogger("paramiko").setLevel(logging_level)  # for example
    app.run(host="0.0.0.0", port=8080)
