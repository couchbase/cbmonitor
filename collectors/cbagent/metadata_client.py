import requests
from logger import logger


def post_request(request):
    def wrapper(*args, **kargs):
        url, params = request(*args, **kargs)
        try:
            r = requests.post(url, params)
        except requests.exceptions.ConnectionError:
            logger.interrupt("Connection error: {0}".format(url))
        else:
            if r.status_code == 500:
                logger.interrupt("Internal server error: {0}".format(url))
    return wrapper


class MetadataClient(object):

    def __init__(self, settings):
        self.settings = settings
        self.base_url = "http://{0}:{1}/cbmonitor"\
            .format(settings.cbmonitor_host, settings.cbmonitor_port)

    @post_request
    def add_cluster(self):
        logger.info("Adding cluster: {0}".format(self.settings.cluster))

        url = self.base_url + "/add_cluster/"
        params = {"name": self.settings.cluster,
                  "rest_username": self.settings.rest_username,
                  "rest_password": self.settings.rest_password}
        return url, params

    @post_request
    def add_server(self, address):
        logger.info("Adding server: {0}".format(address))

        url = self.base_url + "/add_server/"
        params = {"address": address,
                  "cluster": self.settings.cluster,
                  "ssh_username": self.settings.ssh_username,
                  "ssh_password": self.settings.ssh_password}
        return url, params

    @post_request
    def add_bucket(self, name):
        logger.info("Adding bucket: {0}".format(name))

        url = self.base_url + "/add_bucket/"
        params = {"name": name, "type": "Couchbase",
                  "cluster": self.settings.cluster}
        return url, params

    @post_request
    def add_metric(self, name, bucket=None, server=None, unit=None,
                   description=None, collector=None):
        logger.info("Adding metric: {0}".format(name))

        url = self.base_url + "/add_metric_or_event/"
        params = {"name": name, "type": "metric",
                  "cluster": self.settings.cluster}
        for extra_param in ("bucket", "server", "unit", "description",
                            "collector"):
            if eval(extra_param) is not None:
                params[extra_param] = eval(extra_param)
        return url, params

    @post_request
    def add_snapshot(self, name, ts_from, ts_to):
        logger.info("Adding snapshot: {0}".format(name))

        url = self.base_url + "/add_snapshot/"
        params = {"cluster": self.settings.cluster, "name": name,
                  "ts_from": ts_from, "ts_to": ts_to}
        return url, params
