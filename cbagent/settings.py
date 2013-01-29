from argparse import ArgumentParser
from ConfigParser import ConfigParser

from cbagent.stores.seriesly_store import SerieslyStore


class Settings(object):

    def __init__(self):
        config = self._get_cfg()

        self.interval = config.getint("store", "interval")
        self.seriesly_host = config.get("store", "host")
        self.seriesly_database = config.get("store", "database")

        self.master_node = config.get("target", "master_node")
        self.cluster = config.get("target", "cluster")
        self.rest_username = config.get("target", "rest_username")
        self.rest_password = config.get("target", "rest_password")
        self.ssh_username = config.get("target", "ssh_username")
        self.ssh_password = config.get("target", "ssh_password")

        self._set_store()

    @staticmethod
    def _get_cfg():
        parser = ArgumentParser()
        parser.add_argument("config", help="name of configuration file")
        args = parser.parse_args()

        config = ConfigParser()
        config.read(args.config)
        return config

    def _set_store(self):
        self.store = SerieslyStore(self.seriesly_host, self.seriesly_database)
