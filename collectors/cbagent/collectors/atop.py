from cbagent.collectors.libstats.atopstats import AtopStats
from cbagent.collectors import Collector


class Atop(Collector):

    _METRICS = ("beam.smp_rss", "memcached_rss", "beam.smp_vsize",
                "memcached_vsize", "beam.smp_cpu", "memcached_cpu")

    def __init__(self, settings):
        super(Atop, self).__init__(settings)
        self.ssh_username = settings.ssh_username
        self.ssh_password = settings.ssh_password
        self.atop = AtopStats(hosts=tuple(self._get_nodes()),
                              user=settings.ssh_username,
                              password=settings.ssh_password)

    def restart(self):
        self.atop.restart_atop()

    def update_columns(self):
        self.atop.update_columns()

    def update_metadata(self):
        self.mc.add_cluster()
        for node in self._get_nodes():
            self.mc.add_server(node)
            for metric in self._METRICS:
                self.mc.add_metric(metric, server=node)

    @staticmethod
    def _remove_value_units(value):
        for magnitude, denotement in enumerate(("K", "M", "G"), start=1):
            if denotement in value:
                return float(value.replace(denotement, "")) * 1024 ** magnitude
        if "%" in value:
            return float(value.replace("%", ""))
        else:
            return float(value)

    def _format_data(self, data):
        sample = dict()
        for node, (title, value) in data.iteritems():
            sample[node] = sample.get(node, dict())
            sample[node][title] = self._remove_value_units(value)
        return sample

    def _extend_samples(self, data):
        data = self._format_data(data)
        if not self._samples:
            self._samples = data
        else:
            for node in self._samples:
                self._samples[node].update(data[node])

    def collect(self):
        self._samples = {}
        self._extend_samples(self.atop.get_process_rss("beam.smp"))
        self._extend_samples(self.atop.get_process_vsize("beam.smp"))
        self._extend_samples(self.atop.get_process_rss("memcached"))
        self._extend_samples(self.atop.get_process_vsize("memcached"))
        self._extend_samples(self.atop.get_process_cpu("beam.smp"))
        self._extend_samples(self.atop.get_process_cpu("memcached"))

        for node, samples in self._samples.iteritems():
            meta = {"cluster": self.cluster,
                    "server": node,
                    "bucket": "none"}
            self.store.append({"meta": meta, "samples": samples})
