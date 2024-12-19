import flask

import conf
import main

# polled config
sync_blueprint = flask.Blueprint('sync', __name__)


@sync_blueprint.route("/get_config/<user>")
def config(user):
    if user not in conf.users:
        return 'not a user', 400
    for element in conf.trackme:
        computer = element['computer']
        ssh = main.get_connection(computer)
        config = main.get_user_config(user, computer, ssh)
    return usage
