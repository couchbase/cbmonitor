#!/usr/bin/env python

import logging
from collector import Collector
from mc_source import MemcachedSource

class MemcachedCollector(Collector):
    """
    Collect memcached stats across the cluster, \
    optionally process results and emit to the data handlers.
    """

    def __init__(self, sources=None, handlers=None):
        self.sources = sources      # [@class MemcachedSource]
        self.handlers = handlers    # [@class Handler]

    def collect(self):
        """
        Collect stats from data sources
        """
        if not self.sources or \
            not isinstance(self.sources, list):
            logging.error("invalid sources: must be a list")
            return False

        for source in self.sources:
            if not isinstance(source, MemcachedSource):
                logging.error("not a MemcachedSource, skipped")
                continue

            logging.info(
                "collecting mc stats from server %s" %source.server.ip)
            source.connect()
            source.feed()
            source.disconnect()

    def process(self):
        raise NotImplementedError(
            "Do not alter memcached stats")

    def emit(self):
        """
        Emit stats to data handlers
        """
        if not self.handlers or \
            not isinstance(self.handlers, list):
            logging.error("invalid handlers: must be a list")
            return False

        for handler in self.handlers:
            for source in self.sources:
                handler.handle(source)