from fabric.api import hide, settings
from fabric.tasks import execute


def multi_node_task(task):
    def wrapper(*args, **kargs):
        self = args[0]
        with hide("output"):
            with settings(user=self.user, password=self.password,
                          warn_only=True):
                return execute(task, *args, hosts=self.hosts, **kargs)
    return wrapper


def single_node_task(task):
    def wrapper(*args, **kargs):
        self = args[0]
        with hide("output"):
            with settings(host_string=self.hosts[0], user=self.user,
                          password=self.password, warn_only=True):
                return task(*args, **kargs)
    return wrapper


class RemoteStats(object):

    def __init__(self, hosts, user, password):
        self.hosts = hosts
        self.user = user
        self.password = password
