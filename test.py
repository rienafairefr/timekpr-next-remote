import conf
import main


def go():
    print("timetkpr-next-remote started")

    # todo - this should allow for more than one user per IP
    for tracked in conf.trackme:
        users = tracked['users']
        host = tracked['host']
        label = tracked.get('label', host)
        for user in users:
            try:
                ssh = main.get_connection(host)
                main.get_usage(user, host, ssh)
                main.increase_time(100, ssh, user, host, label)
                main.get_usage(user, host, ssh)
                main.decrease_time(100, ssh, user, host, label)
                main.get_usage(user, host, ssh)
            except:
                pass


if __name__ == "__main__":
    go()
