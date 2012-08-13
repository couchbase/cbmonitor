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

        ret = {}
        for key in MemcachedSource.MC_STATS:
            try:
                if key != "":
                    ret[key] = self.mc.stats(key)
                else:
                    ret["all"] = self.mc.stats(key)
            except Exception, e:
                logging.error("exception for key %s : %s" % (key, e))

        return ret

    def disconnect(self):
        self.mc.close()