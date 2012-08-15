#!/usr/bin/env python

import logging
from source import Source
from server import Server

from lib.memcached.helper.data_helper import MemcachedClientHelper

class MemcachedSource(Source):

    MC_STATS = ["", "allocator", "checkpoint", "config", "dispatcher",
                "hash", "kvstore", "kvtimings", "memory", "prev-vbucket",
                "tap", "tapagg", "timings", "vbucket", "vbucket-details"]

    def __init__(self, server, bucket, mc=None):
        self.server = server        # @class: Server
        self.bucket = bucket
        self.mc = mc
        self.data = {}

    def connect(self):
        if not self.server or \
            not isinstance(self.server, Server):
            return False

        self.mc = MemcachedClientHelper.direct_client(
            self.server, self.bucket)

        return True

    def feed(self):
        if not self.mc and not self.connect():
            logging.error("unable to connect to server : %s" % self.server)
            return None

        self.data = {}
        for key in MemcachedSource.MC_STATS:
            try:
                if key != "":
                    self.data[key] = self.mc.stats(key)
                else:
                    self.data["all"] = self.mc.stats(key)
            except Exception, e:
                logging.error("exception for key %s : %s" % (key, e))

        return self.data

    def disconnect(self):
        self.mc.close()

    def gen_stats(self):
        """
        generate individual stats
        @note: no safety check, since we know what the data looks like
        """
        for data in self.data.itervalues():
            for key_val in data.iteritems():
                yield key_val