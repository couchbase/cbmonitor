import requests

from cbagent.metadata_client import MetadataClient


class Collector(object):

    def __init__(self, settings):
        self.cluster = settings.cluster
        self.capi = "http://{0}:8091".format(settings.master_node)
        self.auth = (settings.rest_username, settings.rest_password)
        self.store = settings.store
        self.mc = MetadataClient(settings)

    def _get(self, url):
        """HTTP GET requests with basic authentication"""
        return requests.get(url=self.capi + url, auth=self.auth).json()

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
