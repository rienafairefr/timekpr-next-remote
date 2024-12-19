import logging

import flask
from flask import render_template

import conf
import main

logger = logging.getLogger(__name__)

def validate_request(computer, user):
    logger.info(conf.trackme)
    for element in conf.trackme:
        if element['computer'] == computer:
            break
    else:
        return False, "host not in config"
    if user not in element['users']:
        return False, "user not in host in config"
    else:
        return True, element


admin_blueprint = flask.Blueprint('admin', __name__)


@admin_blueprint.route("/config")
def config():
    return main.get_config()


@admin_blueprint.route("/")
def index():
    return render_template("index.html")


@admin_blueprint.route("/get_usage/<computer>/<user>")
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


@admin_blueprint.route("/increase_time/<computer>/<user>/<seconds>")
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


@admin_blueprint.route("/decrease_time/<computer>/<user>/<seconds>")
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


@admin_blueprint.route("/set_time/<computer>/<user>/<seconds>")
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
