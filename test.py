import main
import conf, re
from fabric import Connection
from paramiko.ssh_exception import AuthenticationException


def go():
    print("timetkpr-next-remote started")

    # todo - this should allow for more than one user per IP
    for ip in conf.trackme.keys():
        users = conf.trackme[ip]
        for user in users:
            try:
                ssh = main.get_connection(ip)
                main.get_usage(user, ip, ssh)
                main.increase_time(100, ssh, user, ip)
                main.get_usage(user, ip, ssh)
                main.decrease_time(100, ssh, user, ip)
                main.get_usage(user, ip, ssh)
            except:
                pass


if __name__ == "__main__":
    go()
