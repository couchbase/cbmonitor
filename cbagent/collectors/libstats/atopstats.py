from uuid import uuid4

from fabric.api import run

from systemstats import SystemStats, multi_task, single_task


uhex = lambda: uuid4().hex


class AtopStats(SystemStats):

    def __init__(self, hosts, user, password):
        super(AtopStats, self).__init__(hosts, user, password)
        self.logfile = "/tmp/{0}.atop".format(uhex())

        self._base_cmd =\
            "d=`date +%H:%M` && atop -r {0} -b $d -e $d".format(self.logfile)
        self._cpu_column = self._get_cpu_column()
        self._vsize_column = self._get_vsize_column()
        self._rss_column = self._get_rss_column()

    @multi_task
    def stop_atop(self):
        run("killall -q atop")
        run("rm -rf {0}".format(self.logfile))

    @multi_task
    def start_atop(self):
        run("nohup atop -a -w {0} 5 > /dev/null 2>&1 &".format(self.logfile))

    def is_atop_running(self):
        raise NotImplementedError

    def restart_atop(self):
        self.stop_atop()
        self.start_atop()

    @single_task
    def _get_vsize_column(self):
        output = run("atop -m 1 1 | grep PID")
        return output.split().index("VSIZE")

    @single_task
    def _get_rss_column(self):
        output = run("atop -m 1 1 | grep PID")
        return output.split().index("RSIZE")

    @single_task
    def _get_cpu_column(ip):
        output = run("atop 1 1 | grep PID")
        return output.split().index("CPU")

    @multi_task
    def get_process_cpu(self, process):
        cmd = self._base_cmd + "| grep {0}".format(process)
        output = run(cmd)
        return output.split()[self._cpu_column]

    @multi_task
    def get_process_vzize(self, process):
        cmd = self._base_cmd + " -m | grep {0}".format(process)
        output = run(cmd)
        return output.split()[self._vsize_column]

    @multi_task
    def get_process_rss(self, process):
        cmd = self._base_cmd + " -m | grep {0}".format(process)
        output = run(cmd)
        return output.split()[self._rss_column]
