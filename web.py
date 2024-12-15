import logging
import os

from flask import Flask, render_template, send_from_directory
import conf
import main

logger = logging.getLogger(__name__)

app = Flask(__name__)

def validate_request(computer, user):
    for element in conf.trackme:
        if element['computer'] == computer:
            break
    else:
        return False, "host not in config"
    if user not in element['users']:
        return False, "user not in host in config"
    else:
        return True, element

@app.route("/config")
def config():
    return main.get_config()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_usage/<computer>/<user>")
def get_usage(computer, user):
    valid, element = validate_request(computer, user)
    if not valid:
        return element, 400
    ssh = main.get_connection(computer)
    usage = main.get_usage(user, computer, ssh)
    return {
        "result": usage["result"],
        "time_left": usage["time_left"],
        "time_spent": usage["time_spent"],
    }, 200


@app.route("/increase_time/<computer>/<user>/<seconds>")
def increase_time(computer, user, seconds):
    valid, element = validate_request(computer, user)
    if not valid:
        return element, 400
    label = element.get('label', computer)
    ssh = main.get_connection(computer)
    if main.increase_time(seconds, ssh, user, computer, label):
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
    valid, element = validate_request(computer, user)
    if not valid:
        return element, 500
    label = element.get('label', computer)
    ssh = main.get_connection(computer)
    if main.decrease_time(seconds, ssh, user, computer, label):
        usage = main.get_usage(user, computer, ssh)
        return {
            "result": "success",
            "time_left": usage["time_left"],
            "time_spent": usage["time_spent"],
        }, 200
    else:
        return {"result": "fail"}, 500


@app.route("/set_time/<computer>/<user>/<seconds>")
def set_time(computer, user, seconds):
    valid, element = validate_request(computer, user)
    if not valid:
        return element, 400
    label = element.get('label', computer)
    ssh = main.get_connection(computer)
    if main.set_time(seconds, ssh, user, computer, label):
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
