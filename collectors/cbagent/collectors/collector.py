import requests

from cbagent.stores.seriesly_store import SerieslyStore
from cbagent.metadata_client import MetadataClient
from cbagent.decorators import json


class Collector(object):

    def __init__(self, settings):
        self.cluster = settings.cluster
        self.master_node = settings.master_node
        self.auth = (settings.rest_username, settings.rest_password)
        self.store = SerieslyStore(settings.seriesly_host,
                                   settings.seriesly_database)
        self.mc = MetadataClient(settings)

    @json
    def _get(self, path, server=None, port=8091):
        """HTTP GET request to Couchbase server with basic authentication"""
        url = "http://{0}:{1}{2}".format(server or self.master_node, port, path)
        return requests.get(url=url, auth=self.auth)

    def _get_buckets(self):
        """Yield bucket names and stats metadata"""
        buckets = self._get("/pools/default/buckets")
        for bucket in buckets:
            yield bucket["name"], bucket["stats"]

    def _get_nodes(self):
        """Yield name of nodes in cluster"""
        pool = self._get("/pools/default")
        for node in pool["nodes"]:
            yield node["hostname"].split(":")[0]

    def collect(self):
        raise NotImplementedError

    def update_metadata(self):
        raise NotImplementedError
