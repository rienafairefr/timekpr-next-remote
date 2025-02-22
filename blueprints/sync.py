import json
import queue

import flask
from flask import request

sync_blueprint = flask.Blueprint('sync', __name__)


class MessageAnnouncer:
    def __init__(self):
        self.listeners = []

    def listen(self):
        self.listeners.append(queue.Queue(maxsize=5))
        return self.listeners[-1]

    def announce(self, msg):
        # We go in reverse order because we might have to delete an element, which will shift the
        # indices backward
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]


announcer = MessageAnnouncer()


@sync_blueprint.route("/connect", methods=["POST"])
def connect():
    try:
        host = str(request.json['host'])
        message_auth = request.headers['Message-Auth']
    except:
        return "Bad request", 400

    announcer.announce({
        'type': 'connect',
        'host': host
    })
    return '', 200


def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg


@sync_blueprint.route('/stream', methods=['GET'])
def listen():
    try:
        request_host = str(request.args['host'])
    except:
        return "Bad request", 400

    def stream():
        yield format_sse(json.dumps({}), 'hello')
        messages = announcer.listen()  # returns a queue.Queue
        yield format_sse(json.dumps({}), 'hello-queue')
        while True:
            msg = messages.get()  # blocks until a new message arrives
            msg_type = msg.pop('type')
            host = msg.pop('host', None)
            if host is not None and host != request_host:
                continue

            yield format_sse(json.dumps(msg), msg_type)

    return flask.Response(stream(), mimetype='text/event-stream')
