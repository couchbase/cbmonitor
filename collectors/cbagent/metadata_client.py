from cbagent.decorators import post_request


class MetadataClient(object):

    def __init__(self, settings, host="127.0.0.1"):
        self.settings = settings
        self.base_url = "http://{0}:8000/cbmonitor".format(host)

    @post_request
    def add_cluster(self):
        url = self.base_url + "/add_cluster/"
        params = {"name": self.settings.cluster,
                  "rest_username": self.settings.rest_username,
                  "rest_password": self.settings.rest_password}
        return url, params

    @post_request
    def add_server(self, address):
        url = self.base_url + "/add_server/"
        params = {"address": address,
                  "cluster": self.settings.cluster,
                  "ssh_username": self.settings.ssh_username,
                  "ssh_password": self.settings.ssh_password}
        return url, params

    @post_request
    def add_bucket(self, name):
        url = self.base_url + "/add_bucket/"
        params = {"name": name, "type": "Couchbase",
                  "cluster": self.settings.cluster}
        return url, params

    @post_request
    def add_metric(self, name, bucket=None, server=None, unit=None,
                   description=None, collector=None):
        url = self.base_url + "/add_metric_or_event/"
        params = {"name": name, "type": "metric",
                  "cluster": self.settings.cluster}
        for extra_param in ("bucket", "server", "unit", "description",
                            "collector"):
            if eval(extra_param) is not None:
                params[extra_param] = eval(extra_param)
        return url, params
