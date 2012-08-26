#!/usr/bin/env python

import logging
from sys_helper import is_num

from libcarbon.carbon_key import CarbonKey
from bls_helper import BLSHelper
from server import Server
from mc_source import MemcachedSource
from mc_collector import MemcachedCollector
from carbon_handler import CarbonHandler
from json_handler import JsonHandler
from data_helper import DataHelper

class VisitorCallback(object):
    """
    Callbacks for metadata visitor
    """
    SLOW_STATS_FUNCS = {"status": BLSHelper.show_status,
                        "balanced": BLSHelper.show_balanced}

    def __init__(self, c_feeder):
        self.c_feeder = c_feeder

    def store_fast(self, root, parents, data, meta, coll,
                   key, val, meta_val, meta_inf, level):
        """Store time-series data into fast-changing database"""
        if not self.c_feeder:
            logging.error(
                "unable to store fast changing data : invalid CarbonFeeder")
            return False

        if is_num(val):
            ip = DataHelper.get_ip(root, parents)
            c_key = CarbonKey("ns", ip, key)
            self.c_feeder.feed(c_key, val)

        return True

    def store_slow(self, root, parents, data, meta, coll,
                   key, val, meta_val, meta_inf, level):
        """Store time-series data into slow-changing database"""
        #TODO
        VisitorCallback._show_slow_stats(key, val)
        return True

    def collect_mc_stats(self, root, parents, data, meta, coll,
                         key, val, meta_val, meta_inf, level=0):
        """
        Collect memcached stats
        Dump time series data to carbon and save a json snapshot
        """
        if not isinstance(val, list):
            logging.error(
                "unable to collect mc stats: val must be a list - %s" % val)
            return False

        logging.info("collecting mc stats from %s" % val)

        for server in val:

            try:
                ip, port = server.split(":")
            except (ValueError, AttributeError), e:
                logging.error(
                    "unable to collect mc stats from %s : %s" % (server, e))
                continue

            BLSHelper.add_server(ip)
            mc_server = Server(ip)

            # get bucket name from root and parent nodes
            bucket = DataHelper.get_bucket(root, parents)

            # initialize memcached source
            mc_source = MemcachedSource(mc_server, bucket)

            # initialize handlers to dump data to carbon and json doc
            c_handler = CarbonHandler(c_feeder=self.c_feeder)
            j_handler = JsonHandler()

            # collect data from source and emit to handlers
            mc_coll = MemcachedCollector([mc_source], [c_handler, j_handler])
            mc_coll.collect()
            mc_coll.emit()

    @staticmethod
    def _show_slow_stats(key, val):
        """
        Show slow changing stats on cbtop
        Dispatch to handling function based on @dict SLOW_STATS_FUNCS
        """
        func = VisitorCallback.SLOW_STATS_FUNCS.get(key, None)
        if not func:
            logging.error("failed to find func to show "\
                          "slow changing stats: %s - %s" % (key, val))
            return

        func(val)
