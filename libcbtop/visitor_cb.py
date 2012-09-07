#!/usr/bin/env python

import logging
from sys_helper import is_num

from tabula.table import Table
from tabula.section import Section

from libcarbon.carbon_key import CarbonKey
from bls_helper import BLSHelper
from server import Server
from mc_source import MemcachedSource
from mc_collector import MemcachedCollector
from carbon_handler import CarbonHandler
from json_handler import JsonHandler
from data_helper import DataHelper

# configuration for each tabula.section
SECTION_CONFIG = {"settings": {"show_row_hdrs": False,
                               "show_col_hdrs": False,
                               "show_col_hdr_in_cell": True},
                  "storage": {"show_row_hdrs": False,
                               "show_col_hdrs": False,
                               "show_col_hdr_in_cell": True},
                  "nodes": {"show_row_hdrs": False,
                            "show_col_hdrs": True,
                            "show_col_hdr_in_cell": False}}

class VisitorCallback(object):
    """
    Callbacks for metadata visitor
    """
    def __init__(self, c_feeder, tbl):
        self.c_feeder = c_feeder
        self.tbl = tbl
        self.cur_row = {}      # {sec_nam: row name}

    def _show_stats(self, key, val, meta_inf):
        """
        Show stats on the ascii table
        """
        if not self.tbl or not isinstance(self.tbl, Table):
            return False

        if not meta_inf or not "section" in meta_inf:
            logging.error(
                "unable to show slow data: key %s, val %s, invalid meta info"
                % (key, val))
            return False

        # ok, not deal with unicode for now
        sec_nam = str(meta_inf["section"])
        val = str(val)

        section = self.tbl.get_section(sec_nam)

        if not section:
            section = Section(sec_nam)
            if sec_nam in SECTION_CONFIG:
                config = SECTION_CONFIG[sec_nam]
                section.config(config["show_row_hdrs"],
                               config["show_col_hdrs"],
                               config["show_col_hdr_in_cell"])
            self.tbl.add_section(section)

        if "col" in meta_inf:
            col = str(meta_inf["col"])
        else:
            col = str(key)

        if "new_row" in meta_inf:
            # create a new row using the col name
            section.add_cell(val, col, val, "S50")
            self.cur_row[sec_nam] = val
            return True

        if not sec_nam in self.cur_row:
            logging.debug("stats %s is not associated with a section" % key)
            return True

        row = self.cur_row[sec_nam]
        section.add_cell(row, col, val, type="S50")

        return True

    def store_fast(self, root, parents, data, meta, coll,
                   key, val, meta_val, meta_inf, level):
        """Store time-series data into fast-changing database"""
        return self._show_stats(key, val, meta_inf)

    def store_slow(self, root, parents, data, meta, coll,
                   key, val, meta_val, meta_inf, level):
        """Store time-series data into slow-changing database"""
        return self._show_stats(key, val, meta_inf)

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