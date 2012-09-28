#!/usr/bin/env python

import logging
import os
import json
from source import Source
from server import Server

from lib.memcached.helper.data_helper import MemcachedClientHelper

class MemcachedSource(Source):

    META_FILE = "%s/../metadata/stats.json" % os.path.dirname(__file__)
    MC_STATS = ["", "allocator", "checkpoint", "config", "dispatcher",
                "hash", "kvstore", "kvtimings", "memory", "prev-vbucket",
                "tap", "tapagg", "timings", "vbucket", "vbucket-details"]

    def __init__(self, server, bucket, meta_file=META_FILE, mc=None):
        self.server = server        # @class: Server
        self.bucket = bucket
        self.mc = mc
        self.data = {}
        self.meta = self.get_meta(meta_file)
        self.slow = {"mc-host": server.ip, "mc-bucket": bucket}
        self.fast = {"mc-host": server.ip, "mc-bucket": bucket}

    def get_meta(self, meta_file):
        with open(meta_file) as f:
            return json.loads(f.read())

    def filter(self, stats):
        if not stats or not self.meta:
            logging.error("unable to apply filter: invalid data or meta")
            return False

        for key in stats:
            mkey = "mc-%s" % key
            if mkey in self.meta and "visit" in self.meta[mkey]:
                if self.meta[mkey]["visit"] == "slow":
                    self.slow[mkey] = stats[key]
                elif self.meta[mkey]["visit"] == "fast":
                    self.fast[mkey] = stats[key]

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
                stats = self.mc.stats(key)
                if key != "":
                    self.data[key] = stats
                else:
                    self.data["all"] = stats
                self.filter(stats)
            except Exception, e:
                logging.error("exception for key %s : %s" % (key, e))

        return self.data

    def disconnect(self):
        self.mc.close()

    def gen_stats(self):
        """
        Generate individual stats
        """
        for data in self.data.itervalues():
            for key_val in data.iteritems():
                yield key_val