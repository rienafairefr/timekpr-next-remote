import logging
import os
import time
from io import StringIO

from fabric import Connection

import conf
import main

logger = logging.getLogger(__name__)
def sync():
    with open('timekpr.conf', 'r') as timekpr_conf_file:
        timekpr_conf = timekpr_conf_file.read()

    users = os.environ.get('USERS_PUSHED', '').split(',')

    timekpr_confs = {}
    for user in users:
        timekpr_confs[user] = StringIO(timekpr_conf.replace('{{user}}', user))

    while True:
        connections = {}
        for user in users:
            time_lefts = []
            for trackme in conf.trackme:
                computer = trackme['computer']

                if user not in trackme['users']:
                    continue

                if computer not in connections:
                    connections[computer] = main.get_connection(computer)
                ssh = connections[computer]

                ok, data = main.do_get_usage(user, computer, ssh)
                if ok:
                    time_left, _ = data
                    time_lefts.append(int(time_left))
            if len(time_lefts) == 0:
                continue
            min_time_left = min(time_lefts)
            logger.info((user, min_time_left, time_lefts))

            for trackme in conf.trackme:
                computer = trackme['computer']

                if user not in trackme['users']:
                    continue

        for ssh in connections.values():
            ssh: Connection
            ssh.close()
        time.sleep(60)
