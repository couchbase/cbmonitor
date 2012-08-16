#!/usr/bin/env python

import logging
from sys_helper import is_num

from handler import Handler
from libcarbon.carbon_feeder import CarbonFeeder
from libcarbon.carbon_key import CarbonKey
from mc_source import MemcachedSource

class CarbonHandler(Handler):
    """
    Handler to dump data to carbon
    """
    def __init__(self, host="127.0.0.1", c_feeder=None):
        self.host = host    # hostname or ip of the carbon server
        self.c_feeder = c_feeder

    def handle(self, source):
        """
        Dump data to carbon
        """
        if not source or \
           not source.data or \
           not self.host:
            logging.error(
                "unable to handle : invalid source or hostname")
            return False

        if not self.c_feeder:
            self.c_feeder = CarbonFeeder(self.host)

        # unpack data and send to carbon
        if isinstance(source, MemcachedSource):
            return self._handle_mc(source)
        else:
            logging.error("unknown source: %s" %source)

    def _handle_mc(self, source):
        if not source or not source.data:
            logging.error("invalid source")
            return False

        if not self.c_feeder:
            logging.error("unable to create carbon feeder")
            return False

        ip = source.server.ip
        for key,val in source.gen_stats():
            if is_num(val):
                c_key = CarbonKey("mc", ip, key)
                self.c_feeder.feed(c_key, val)