from uuid import uuid4

from fabric.api import run, hide, settings
from fabric.tasks import execute

uhex = lambda: uuid4().hex


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


class SystemStats(object):

    def __init__(self, hosts, user, password):
        self.hosts = hosts
        self.user = user
        self.password = password

    @multi_node_task
    def swap_usage(ip):
        output = run("free | grep -i swap")
        swap_usage = {}
        for i, metric in enumerate(("swap_total", "swap_free", "swap_used")):
            swap_usage["swap_" + metric] = output.split()[i + 1]
        return swap_usage

    @multi_node_task
    def mem_usage(ip):
        output = run("free | grep -i mem")
        mem_usage = {}
        for i, metric in enumerate(("total", "used", "free", "shared",
                                    "buffers", "cached")):
            mem_usage["mem_" + metric] = output.split()[i + 1]
        return mem_usage
