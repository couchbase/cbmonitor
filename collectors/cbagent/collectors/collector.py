import requests


class Collector(object):

    def __init__(self, settings):
        self.cluster = settings.cluster
        self.capi = "http://{0}:8091".format(settings.master_node)
        self.auth = (settings.rest_username, settings.rest_password)
        self.store = settings.store

    def _get(self, url):
        return requests.get(url=self.capi + url, auth=self.auth).json()

    def _get_nodes(self):
        pool = self._get("/pools/default")
        for node in pool["nodes"]:
            yield node["hostname"].split(":")[0]

    def collect(self):
        raise NotImplementedError

    def update_metadata(self):
        raise NotImplementedError
