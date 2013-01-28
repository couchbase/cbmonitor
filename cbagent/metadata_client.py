import requests


def post_request(request):
    def wrapper(*args, **kargs):
        url, params = request(*args, **kargs)
        requests.post(url, params)
    return wrapper


class MetadataClient(object):

    def __init__(self, host="127.0.0.1"):
        self.base_url = "http://{0}:8000/cbmonitor".format(host)

    @post_request
    def add_cluster(self, name, rest_username, rest_password):
        url = self.base_url + "/add_cluster/"
        params = {"name": name,
                  "rest_username": rest_username,
                  "rest_password": rest_password}
        return url, params

    @post_request
    def add_server(self, cluster, address):
        url = self.base_url + "/add_server/"
        params = {"cluster": cluster, "address": address}
        return url, params

    @post_request
    def add_bucket(self, cluster, name):
        url = self.base_url + "/add_bucket/"
        params = {"cluster": cluster, "name": name, "type": "Couchbase"}
        return url, params

    @post_request
    def add_metric(self, cluster, name, bucket=None, server=None):
        url = self.base_url + "/add_metric_or_event/"
        params = {"type": "metric", "cluster": cluster, "name": name}
        if server:
            params["server"] = server
        if bucket:
            params["bucket"] = bucket
        return url, params
