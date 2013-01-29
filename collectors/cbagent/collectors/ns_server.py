#!/usr/bin/env python
from cbagent.metadata_client import MetadataClient
from cbagent.collectors.collector import Collector


class NSServer(Collector):

    def _get_buckets(self):
        buckets = self._get("/pools/default/buckets")
        for bucket in buckets:
            yield bucket["name"], bucket["stats"]

    def _get_metrics(self):
        bucket, stats = self._get_buckets().next()
        stats = self._get(stats["directoryURI"])
        for block in stats["blocks"]:
            for metric in block["stats"]:
                yield metric["name"]

    def _last_stats(self, samples):
        return dict((k, v[-1]) for k, v in samples['op']['samples'].iteritems())

    def collect(self):
        for bucket, stats in self._get_buckets():
            uri = stats["uri"]
            samples = self._get(uri)
            data = {
                "metric": {self.cluster: {bucket: self._last_stats(samples)}}
            }
            self.store.append(data)

            stats_list = self._get(stats["nodeStatsListURI"])
            for server in stats_list["servers"]:
                host = server["hostname"].split(":")[0]
                uri = server["stats"]["uri"]
                samples = self._get(uri)
                data = {
                    "metric": {self.cluster: {bucket: {host: self._last_stats(samples)}}}
                }
                self.store.append(data)

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
