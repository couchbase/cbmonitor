#!/usr/bin/env python

import logging
import time

from handler import Handler
from libcarbon.carbon_feeder import CarbonFeeder
from libcarbon.carbon_key import CarbonKey
from mc_source import MemcachedSource

class CarbonHandler(Handler):
    """
    Handler to dump data to carbon
    """
    def __init__(self, host):
        self.host = host    # hostname or ip of the carbon server

    def handle(self, source):
        """
        put data into carbon
        """
        if not source or \
           not source.data or \
           not self.host:
            logging.error(
                "unable to handle : invalid source or hostname")
            return False

        # unpack data and send to carbon
        if isinstance(source, MemcachedSource):
            return self._handle_mc(source)
        else:
            logging.error("unknown source: %s" %source)

    def _handle_mc(self, source):
        if not source or not source.data:
            logging.error("invalid source")
            return False

        c_feeder = CarbonFeeder(self.host)
        if not c_feeder:
            logging.error("unable to create carbon feeder")
            return False

        ip = source.server.ip
        for key_val in source.gen_stats():
            # TODO: tweak the key? reuse connection?
            key, val = key_val
            c_key = CarbonKey("cb", ip, "mc-" + key)
            c_feeder.feed(key, val)