import logging
import os
import tempfile
import time

from fabric import Connection
from timekpr.common.utils.config import timekprUserConfig

import conf
import main

logger = logging.getLogger(__name__)


def sync():
    with open('timekpr.conf', 'r') as timekpr_conf_file:
        timekpr_conf = timekpr_conf_file.read()

    users = os.environ.get('USERS_PUSHED', '').split(',')
    with tempfile.TemporaryDirectory() as config_dir:
        for user in users:
            with open(os.path.join(config_dir, f'timekpr.{user}.conf'), 'w') as config_file:
                config_file.write(timekpr_conf.replace('{{user}}', user))

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

                    user_config = timekprUserConfig(config_dir, user)
                    user_config.loadUserConfiguration()

                    to_send = {
                        'ALLOWED_HOURS_1': f"--setallowedhours {user} 1",
                        'ALLOWED_HOURS_2': f"--setallowedhours {user} 2",
                        'ALLOWED_HOURS_3': f"--setallowedhours {user} 3",
                        'ALLOWED_HOURS_4': f"--setallowedhours {user} 4",
                        'ALLOWED_HOURS_5': f"--setallowedhours {user} 5",
                        'ALLOWED_HOURS_6': f"--setallowedhours {user} 6",
                        'ALLOWED_HOURS_7': f"--setallowedhours {user} 7",
                        'ALLOWED_WEEKDAYS': f"--setalloweddays {user}",
                        'LIMITS_PER_WEEKDAYS': f"--settimelimits {user}",
                        'LIMIT_PER_WEEK': f"--settimelimitweek {user}",
                        'LIMIT_PER_MONTH': f"--settimelimitmonth {user}",
                        'TRACK_INACTIVE': f"--settrackinactive {user}",
                        'HIDE_TRAY_ICON': f"--sethidetrayicon {user}",

                        'PLAYTIME_ENABLED': f"--setplaytimeenabled {user}",
                        'PLAYTIME_LIMIT_OVERRIDE_ENABLED': f"--setplaytimelimitoverride {user}",
                        'PLAYTIME_UNACCOUNTED_INTERVALS_ENABLED': f"--setplaytimeunaccountedintervalsflag {user}",
                        'PLAYTIME_ALLOWED_WEEKDAYS': f"--setplaytimealloweddays {user}",
                        'PLAYTIME_LIMITS_PER_WEEKDAYS': f"--setplaytimelimits {user}",

                        # 'LOCKOUT_TYPE': f"--setlockouttype {user}",
                        # 'WAKEUP_HOUR_INTERVAL': "--setallowedhours",
                    }

                    for key, value in user_config._timekprUserConfig.items():
                        logger.info(f'{key} = {value}')

                    ok, actual_user_info = main.run_with_retry(f"--userinfo {user}", computer, ssh)
                    if ok:
                        logger.info(actual_user_info)
                        actual_user_info_dict = {}

                        for line in actual_user_info.stdout.splitlines():
                            line = line.strip()
                            try:
                                key, value = line.split(': ', maxsplit=1)
                                actual_user_info_dict[key] = value
                            except ValueError:
                                pass

                        for key, value in to_send.items():
                            # noinspection PyProtectedMember
                            config_value = user_config._timekprUserConfig[key]
                            cmd = f"{value} {config_value}"
                            logger.info(('to_send', key, config_value))
                            logger.info(('actual', key, actual_user_info_dict[key]))

                            if actual_user_info_dict[key] != str(config_value):
                                logger.info(('sending', key, config_value))

                            # ok, data = main.run_with_retry(cmd, computer, ssh)
#
                            # if ok:
                            #    logger.info(f'OK pushed {key} ({value})')
                            # else:
                            #    logger.error(f'error {key}')
                            #    logger.error(cmd)

                    ok, user_info = main.run_with_retry(f"--userinfo {user}", computer, ssh)
                    if ok:
                        logger.info(user_info)

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
