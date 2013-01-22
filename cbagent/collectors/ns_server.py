#!/usr/bin/env python
import requests

from cbagent.metadata_client import MetadataClient
from collector import Collector


class NSServer(Collector):

    def __init__(self, host, cluster, store):
        self.store = store
        self.cluster = cluster
        self.root_url = "http://{0}:8091".format(host)

    def _get_nodes(self):
        pool = requests.get(self.root_url + "/pools/default").json()
        for node in pool["nodes"]:
            yield node["hostname"].split(":")[0]

    def _get_buckets(self):
        buckets = requests.get(self.root_url + "/pools/default/buckets").json()
        for bucket in buckets:
            yield bucket["name"], bucket["stats"]

    def _get_metrics(self):
        bucket, stats = self._get_buckets().next()
        stats = requests.get(self.root_url + stats["directoryURI"]).json()
        for block in stats["blocks"]:
            for metric in block["stats"]:
                yield metric["name"]

    def _last_stats(self, samples):
        return dict((k, v[-1]) for k, v in samples['op']['samples'].iteritems())

    def collect(self):
        for bucket, stats in self._get_buckets():
            uri = stats["uri"]
            samples = requests.get(self.root_url + uri).json()
            data = {
                "metric": {self.cluster: {bucket: self._last_stats(samples)}}
            }
            self.store.append(data)

            stats_list = requests.get(self.root_url + stats["nodeStatsListURI"]).json()
            for server in stats_list["servers"]:
                host = server["hostname"].split(":")[0]
                uri = server["stats"]["uri"]
                samples = requests.get(self.root_url + uri).json()
                data = {
                    "metric": {self.cluster: {bucket: {host: self._last_stats(samples)}}}
                }
                self.store.append(data)

    def update_metadata(self):
        mc = MetadataClient()
        mc.add_cluster(self.cluster)
        for bucket, _ in self._get_buckets():
            mc.add_bucket(self.cluster, bucket)
            for metric in self._get_metrics():
                mc.add_metric(self.cluster, metric, bucket)
            for node in self._get_nodes():
                mc.add_server(self.cluster, node)
                for metric in self._get_metrics():
                    mc.add_metric(self.cluster, metric, bucket, node)
