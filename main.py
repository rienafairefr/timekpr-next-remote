# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import logging
import typing
from typing import Tuple

from fabric import Connection
from gotify import Gotify
from invoke import Result
from paramiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError
from tenacity import retry, wait_random_exponential, retry_if_exception_type

import conf
import humanize
import re

logger = logging.getLogger(__name__)


def get_config():
    return conf.trackme


def send_alert(user, action, seconds, host, label, ssh: Connection):
    logger.info(f'send_alert {user=} {action=} {seconds=} {host=} {label=}')
    if not hasattr(conf, 'gotify'):
        return True
    for alerts in conf.gotify:
        if alerts["enabled"] is True:
            gotify = Gotify(
                base_url=alerts["url"],
                app_token=alerts["token"],
            )
            try:
                usage = get_usage(user, host, ssh)
                added = humanize.naturaldelta(seconds)
                unused = humanize.precisedelta(usage["time_left"])
                used = humanize.precisedelta(usage["time_spent"])
                result = gotify.create_message(
                    f"{action} {added}, {unused} unused, {used} used :)",
                    title=f"Timekpr: {user} {action} time",
                    priority=2,
                )
            except Exception as e:
                logger.error(f"Failed to call Gotify. Config is: {alerts}.  Error is: {e}")
                continue
            logger.info(f"Gotify alert sent to {alerts['url']}")
    return True


class Retry(Exception):
    pass


fail_json = {"time_left": 0, "time_spent": 0, "result": "fail"}


@retry(retry=retry_if_exception_type(Retry), wait=wait_random_exponential(multiplier=1.2, max=60))
def run_with_retry(cmd: str, host: str, ssh: Connection) -> Tuple[bool, typing.Union[Result, typing.Dict]]:
    try:
        result = ssh.run(conf.ssh_timekpra_bin + " " + cmd, hide=True)

    except NoValidConnectionsError as e:
        logger.error(
            f"Cannot connect to SSH server on host '{host}'. "
            f"Check address in conf.py or try again later."
        )
        return False, {}
    except AuthenticationException as e:
        logger.error(
            f"Wrong credentials for user '{conf.ssh_user}' on host '{host}'. "
            f"Check ssh_user and ssh_password credentials in conf.py."
        )
        return False, {}
    except Exception as e:
        logger.error(
            f"Error logging in as user '{conf.ssh_user}' on host '{host}', check conf.py. \n\n\t"
            + str(e)
        )
        return False, {}

    if 'is already running for user' in result.stdout:
        raise Retry()

    return True, result

def do_get_usage(user: str, host: str, ssh: Connection):
    ok, result = run_with_retry(f"--userinfo {user}", host, ssh)
    if not ok:
        return ok, fail_json

    timekpra_userinfo_output = str(result)

    search = r"(TIME_LEFT_DAY: )([0-9]+)"
    time_left = re.search(search, result.stdout)
    search = r"(TIME_SPENT_DAY: )([0-9]+)"
    time_spent = re.search(search, result.stdout)

    if 'is already running for user' in result.stdout:
        raise Retry()

    if not time_left or not time_left.group(2):
        logger.error(
            f"Error getting time left, setting to 0. ssh call result: "
            + timekpra_userinfo_output
        )
        return False, fail_json
    time_left = str(time_left.group(2))
    time_spent = str(time_spent.group(2))
    return True, (time_left, time_spent)


def get_usage(user: str, host: str, ssh: Connection):
    # to do - maybe check if user is in timekpr first? (/usr/bin/timekpra --userlist)
    ok, data = do_get_usage(user, host, ssh)
    if not ok:
        return data
    time_left, time_spent = data

    logger.info(f"Time left for {user} at {host}: {time_left}")
    return {"time_left": time_left, "time_spent": time_spent, "result": "success"}


def get_connection(host) -> Connection:
    # todo handle SSH keys instead of forcing it to be passsword only
    connect_kwargs = {
        "allow_agent": False,
        "look_for_keys": False,
        "password": conf.ssh_password,
    }
    try:
        connection = Connection(
            host=host, user=conf.ssh_user, connect_kwargs=connect_kwargs, connect_timeout=10
        )
    except AuthenticationException as e:
        logger.error(
            f"Wrong credentials for user '{conf.ssh_user}' on host '{host}'. "
            f"Check `ssh_user` and `ssh_password` credentials in conf.py."
        )
    except Exception as e:
        logger.error(
            f"Error logging in as user '{conf.ssh_user}' on host '{host}', check conf.py. \n\n\t"
            + str(e)
        )
    finally:
        return connection


def adjust_time(up_down_string, seconds, ssh: Connection, user, host, label):
    command = f'{conf.ssh_timekpra_bin} --settimeleft {user} {up_down_string} {seconds}'
    ssh.run(command)
    if up_down_string == "-":
        action = "removed"
    elif up_down_string == "":
        action = "set"
    else:
        action = "added"
    logger.info(f"{action} {seconds} for user '{user}'")
    try:
        send_alert(user, action, seconds, host, label, ssh)
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")
    # todo - return false if this fails
    return True


def increase_time(seconds, ssh: Connection, user, host, label):
    return adjust_time("+", seconds, ssh, user, host, label)


def decrease_time(seconds, ssh: Connection, user, host, label):
    return adjust_time("-", seconds, ssh, user, host, label)


def set_time(seconds, ssh: Connection, user, host, label):
    return adjust_time("", seconds, ssh, user, host, label)
