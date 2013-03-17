from time import time
from uuid import uuid4

from cbtestlib.memcached.helper.data_helper import VBucketAwareMemcached
from cbtestlib.membase.api.rest_client import RestConnection

from cbagent.collectors import Collector

uhex = lambda: uuid4().hex


class Latency(Collector):

    _METRICS = ("latency_set", "latency_get", "latency_delete")

    def __init__(self, settings):
        super(Latency, self).__init__(settings)
        rest = self._get_rest_connection(settings)
        self.clients = list()
        for bucket in self._get_buckets():
            self.clients.append(VBucketAwareMemcached(rest, bucket))

    @staticmethod
    def _get_rest_connection(settings):
        return RestConnection({
            "ip": settings.master_node,
            "username": settings.rest_username,
            "password": settings.rest_password,
            "port": 8091
        })

    def update_metadata(self):
        self.mc.add_cluster()
        for bucket in self._get_buckets():
            self.mc.add_bucket(bucket)
            for metric in self._METRICS:
                self.mc.add_metric(metric, bucket=bucket, collector="latency")

    @staticmethod
    def _measure_latency(client, metric, key):
        t0 = time()
        if metric == "latency_set":
            client.set(key, 0, 0, key)
        elif metric == "latency_get":
            client.get(key)
        elif metric == "latency_delete":
            client.delete(key)
        return 1000 * (time() - t0)  # Latency in ms

    def collect(self):
        for client in self.clients:
            key = uhex()
            samples = dict(((metric, self._measure_latency(client, metric, key))
                            for metric in self._METRICS))
            self.store.append(samples, cluster=self.cluster,
                              bucket=client.bucket, collector="latency")
