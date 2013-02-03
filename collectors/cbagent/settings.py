from argparse import ArgumentParser
from ConfigParser import ConfigParser

from cbagent.stores.seriesly_store import SerieslyStore


class Settings(dict):

    def __init__(self, options={}):
        for option, value in options.iteritems():
            self.__setattr__(option, value)

    def read_cfg(self):
        parser = ArgumentParser()
        parser.add_argument("config", help="name of configuration file")
        args = parser.parse_args()

        self.config = ConfigParser()
        self.config.read(args.config)

        self.interval = self.config.getint("store", "interval")
        self.seriesly_host = self.config.get("store", "host")
        self.seriesly_database = self.config.get("store", "database")
        self.update_metadata = self.config.getboolean("store", "update_metadata")

    def __getattribute__(self, name):
        if name == "store":
            return SerieslyStore(self.seriesly_host, self.seriesly_database)
        try:
            return super(Settings, self).__getattribute__(name)
        except AttributeError:
            return self.config.get("target", name)

    def __getitem__(self, item):
        return self.__getattribute__(item)
