from argparse import ArgumentParser
from ConfigParser import ConfigParser, NoOptionError

from logger import logger


class DefaultSettings(dict):

    def __init__(self):
        self.cbmonitor_host = "127.0.0.1"
        self.cbmonitor_port = 8000

        self.interval = 10
        self.seriesly_host = "127.0.0.1"
        self.update_metadata = False

        self.cluster = "default"
        self.master_node = "127.0.0.1"
        self.rest_username = "Administrator"
        self.rest_password = "password"
        self.ssh_username = "root"
        self.ssh_password = "couchbase"


class Settings(DefaultSettings):

    def __init__(self, options={}):
        super(Settings, self).__init__()
        for option, value in options.iteritems():
            setattr(self, option, value)

    def read_cfg(self):
        parser = ArgumentParser()
        parser.add_argument("config", help="name of configuration file")
        args = parser.parse_args()

        config = ConfigParser()
        try:
            logger.info("Reading configuration file: {0}".format(args.config))
            config.read(args.config)
            logger.info("Configuration file successfully parsed")
        except Exception as e:
            logger.interrupt("Failed to parse config file: {0}".format(e))
        try:
            self.cbmonitor_host = config.get("cbmonitor", "host")
            self.cbmonitor_port = config.getint("cbmonitor", "port")

            self.interval = config.getint("store", "interval")
            self.seriesly_host = config.get("store", "host")
            self.update_metadata = config.getboolean("store", "update_metadata")

            self.cluster = config.get("target", "cluster")
            self.master_node = config.get("target", "master_node")
            self.rest_username = config.get("target", "rest_username")
            self.rest_password = config.get("target", "rest_password")
            self.ssh_username = config.get("target", "ssh_username")
            self.ssh_password = config.get("target", "ssh_password")
        except NoOptionError as e:
            logger.interrupt("Failed to get option from config: {0}".format(e))

        logger.info("Configuration file successfully applied")

    def __getitem__(self, item):
        return getattr(self, item, None)
