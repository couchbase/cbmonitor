from eventlet import GreenPool

from cbagent.collectors import Collector


class NSServer(Collector):

    def __init__(self, settings):
        super(NSServer, self).__init__(settings)
        self.pool = GreenPool()

    def _get_buckets(self):
        """Yield bucket names and stats metadata"""
        buckets = self._get("/pools/default/buckets")
        for bucket in buckets:
            yield bucket["name"], bucket["stats"]

    def _get_stats_uri(self):
        """Yield stats URIs"""
        for bucket, stats in self._get_buckets():
            uri = stats["uri"]
            yield uri, bucket, None  # cluster wide

            stats_list = self._get(stats["nodeStatsListURI"])
            for server in stats_list["servers"]:
                host = server["hostname"].split(":")[0]
                uri = server["stats"]["uri"]
                yield uri, bucket, host  # server specific

    def _get_samples(self, uri):
        """Fetch and reduce stats taking only last sample for every metric"""
        samples = self._get(uri)  # get last minute samples
        return dict((k, v[-1]) for k, v in samples['op']['samples'].iteritems())

    def _get_stats(self, (uri, bucket, host)):
        """Generate stats dictionary (json document)"""
        samples = self._get_samples(uri)
        return samples, host, bucket

    def sample(self):
        """Sample all available stats from ns_server"""
        for stats, host, bucket in self.pool.imap(self._get_stats,
                                                  self._get_stats_uri()):
            self.store.append(stats, self.cluster, host, bucket, "ns_server")

    def _get_metrics(self):
        """Yield names of metrics for every bucket"""
        nodes = list(self._get_nodes())
        for bucket, stats in self._get_buckets():
            stats_directory = self._get(stats["directoryURI"])
            for block in stats_directory["blocks"]:
                for metric in block["stats"]:
                    yield metric["name"], bucket, None, metric["desc"]
                    for node in nodes:
                        yield metric["name"], bucket, node, metric["desc"]

    def update_metadata(self):
        """Update cluster's, server's and bucket's metadata"""
        self.mc.add_cluster()

        for bucket in super(NSServer, self)._get_buckets():
            self.mc.add_bucket(bucket)

        for node in self._get_nodes():
            self.mc.add_server(node)

        for metric, bucket, node, desc in self._get_metrics():
            self.mc.add_metric(metric, bucket=bucket, server=node,
                               description=desc, collector="ns_server")
