import requests
import ujson as json

from cbagent.stores.seriesly_store import SerieslyStore
from cbagent.metadata_client import MetadataClient


class Collector(object):

    def __init__(self, settings):
        self.cluster = settings.cluster
        self.master_node = settings.master_node
        self.auth = (settings.rest_username, settings.rest_password)
        self.store = SerieslyStore(settings.seriesly_host,
                                   settings.seriesly_database)
        self.mc = MetadataClient(settings)

    def _get(self, path):
        """HTTP GET requests with basic authentication (web administration
        port)"""
        url = "http://{0}:8091{1}".format(self.master_node, path)
        response = requests.get(url=url, auth=self.auth).text
        return json.loads(response)

    def _get_capi(self, server, path):
        """HTTP GET requests with basic authentication (Couchbase API port)"""
        url = 'http://{0}:8092{1}'.format(server, path)
        response = requests.get(url=url, auth=self.auth).text
        return json.loads(response)

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
