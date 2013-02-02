from eventlet import GreenPool

from cbagent.metadata_client import MetadataClient
from cbagent.collectors.collector import Collector


class NSServer(Collector):

    def __init__(self, settings):
        super(NSServer, self).__init__(settings)
        self.pool = GreenPool()

    def _get_buckets(self):
        """Yield bucket names and stats metadata"""
        buckets = self._get("/pools/default/buckets")
        for bucket in buckets:
            yield bucket["name"], bucket["stats"]

    def _get_metrics(self):
        bucket, stats = self._get_buckets().next()
        stats = self._get(stats["directoryURI"])
        for block in stats["blocks"]:
            for metric in block["stats"]:
                yield metric["name"]

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
        if host:
            return {"metric": {self.cluster: {bucket: {host: samples}}}}
        else:
            return {"metric": {self.cluster: {bucket: samples}}}

    def collect(self):
        """Collect all available stata from ns_server"""
        for stats in self.pool.imap(self._get_stats, self._get_stats_uri()):
            self.store.append(stats)

    def update_metadata(self):
        mc = MetadataClient()
        mc.add_cluster(self.cluster, self.auth[0], self.auth[1])
        for bucket, _ in self._get_buckets():
            mc.add_bucket(self.cluster, bucket)
            for metric in self._get_metrics():
                mc.add_metric(self.cluster, metric, bucket)
            for node in self._get_nodes():
                mc.add_server(self.cluster, node)
                for metric in self._get_metrics():
                    mc.add_metric(self.cluster, metric, bucket, node)
