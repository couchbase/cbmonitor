from uuid import uuid4

from fabric.api import run

from cbagent.collectors.libstats.decorators import multi_node_task


uhex = lambda: uuid4().hex


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
