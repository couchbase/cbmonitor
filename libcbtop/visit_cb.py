#!/usr/bin/env python
import logging
import json
import time
import multiprocessing
import Queue

from lib.membase.api.rest_client import RestConnection
from lib.membase.api.exception import ServerUnavailableException

from tabula.table import Table
from tabula.section import Section
from seriesly import Seriesly
import seriesly.exceptions

from metadata.visit import retrieve_meta

from paint import TABULA_CONV_FUNCS, TABULA_DECO_FUNCS
from server import Server
from mc_source import MemcachedSource
from mc_collector import MemcachedCollector
from json_handler import JsonHandler
from seriesly_handler import SerieslyHandler
from data_helper import DataHelper

# configuration for each tabula.section
SECTION_CONFIG = {"settings": {"id": 0,
                               "show_row_hdrs": False,
                               "show_col_hdrs": False,
                               "show_col_hdr_in_cell": True},
                  "storage": {"id": 1,
                              "show_row_hdrs": False,
                              "show_col_hdrs": False,
                              "show_col_hdr_in_cell": True},
                  "buckets": {"id": 2,
                            "show_row_hdrs": False,
                            "show_col_hdrs": True,
                            "show_col_hdr_in_cell": False},
                  "nodes": {"id": 3,
                            "show_row_hdrs": False,
                            "show_col_hdrs": True,
                            "show_col_hdr_in_cell": False},
                  "Memory Stats": {"id": 4,
                                     "show_row_hdrs": False,
                                     "show_col_hdrs": True,
                                     "show_col_hdr_in_cell": False}}

tbl = Table("cbtop", sep=" ")
cur_row = {}      # {sec_nam: row name}
mc_jobs = multiprocessing.Queue(1)
mc_stats = multiprocessing.Queue(20)
store = None

class SerieslyStore(object):

    def __init__(self, host, dbslow, dbfast):
        self.slow = {}
        self.fast = {}
        self.dbslow = dbslow
        self.dbfast = dbfast
        self.seriesly = Seriesly(host=host)
        try:
            dbs = self.seriesly.list_dbs()
        except seriesly.exceptions.ConnectionError, e:
            logging.error("unable to connect to seriesly server: %s" % e)
            return

        if dbslow not in dbs:
            self.seriesly.create_db(dbslow)
        if dbfast not in dbs:
            self.seriesly.create_db(dbfast)

    def clear(self):
        self.slow = {}
        self.fast = {}

    def add_fast(self, key, val):
        self.fast[key] = val

    def add_slow(self, key, val):
        self.slow[key] = val

    def persist(self):
        try:
            if self.slow:
                self.seriesly[self.dbslow].append(self.slow)
            if self.fast:
                self.seriesly[self.dbfast].append(self.fast)
        except seriesly.exceptions.ConnectionError, e:
            logging.error("unable to connect to seriesly server: %s" % e)
            return False

        return True

def _show_stats(key, val, meta_inf):
    """
    Show stats on the ascii table
    """
    if not tbl or not isinstance(tbl, Table):
        return False

    if not meta_inf or not "section" in meta_inf:
        logging.debug("unable to show data: key %s, val %s, invalid meta info"
                      % (key, val))
        return False

    # ok, not deal with unicode for now
    sec_nam = str(meta_inf["section"])
    val = str(val)

    section = tbl.get_section(sec_nam)

    if not section:
        if sec_nam in SECTION_CONFIG:
            config = SECTION_CONFIG[sec_nam]
            section = Section(sec_nam, config["id"],
                              conv_funcs=TABULA_CONV_FUNCS,
                              deco_funcs=TABULA_DECO_FUNCS)
            section.config(config["show_row_hdrs"],
                config["show_col_hdrs"],
                config["show_col_hdr_in_cell"])
        else:
            return False
        tbl.add_section(section)

    if "col" in meta_inf:
        col = str(meta_inf["col"])
    else:
        col = str(key)

    if "new_row" in meta_inf:
        # create a new row using the col name
        section.add_cell(val, col, val, "S50", meta=meta_inf)
        cur_row[sec_nam] = val
        return True

    if not sec_nam in cur_row:
        logging.debug("stats %s is not associated with a section" % key)
        return True

    row = cur_row[sec_nam]
    section.add_cell(row, col, val, type="S50", meta=meta_inf)

    return True

def show_all_stats(stats, meta):
    if not isinstance(stats, dict) or not isinstance(meta, dict):
        logging.error("failed to show all stats : invalid data")
        return False

    for key, val in stats.iteritems():
        if not key in meta:
            continue

        _show_stats(key, val, meta[key])

def store_fast(root, parents, data, meta, coll,
               key, val, meta_val, meta_inf, level):
    """Store time-series data into fast-changing database"""
    store.add_fast(key, val)
    return _show_stats(key, val, meta_inf)

def store_slow(root, parents, data, meta, coll,
               key, val, meta_val, meta_inf, level):
    """Store time-series data into slow-changing database"""
    store.add_slow(key, val)
    return _show_stats(key, val, meta_inf)

def url_before(context, path):
    return context, path

def url_after(context, path, root):
    pass

def retrieve_data(context, path):
    """Retrieve json data from a couchbase server through REST calls"""
    # TODO: use cbtestlib
    server = Server(context.get("host", "127.0.0.1"))
    rest = RestConnection(server)
    api = rest.baseUrl + path

    try:
        status, content, header = rest._http_request(api)   #TODO: expose
    except ServerUnavailableException, e:
        logging.error("unable to retrieve data from %s: %s" % (server, e))
        return retrieve_meta(context, path)

    if status:
        return json.loads(content)

    return retrieve_meta(context, path)

def collect_mc_stats(root, parents, data, meta, coll,
                     key, val, meta_val, meta_inf, level=0):
    """
    Collect memcached stats
    Dump time series data a json snapshot
    """
    if not isinstance(val, list):
        logging.error(
            "unable to collect mc stats: val must be a list - %s" % val)
        return False

    try:
        stats, meta = mc_stats.get(block=False)
        show_all_stats(stats, meta)
    except Queue.Empty:
        pass

    try:
        mc_jobs.put([root, parents, val], block=False)
        return True
    except Queue.Full:
        logging.debug("unable to collect mcstats : queue is full")
        return False

def mc_worker(jobs, stats, ctl, store, timeout=5):
    logging.info("mc_worker started")

    while ctl["run_ok"]:
        try:
            root, parents, val = jobs.get(block=True, timeout=timeout)
        except Queue.Empty:
            logging.debug("mc_worker hasn't received jobs for %s seconds"
                          % timeout)
            continue

        start = time.time()

        for server in val:

            try:
                ip, port = server.split(":")
            except (ValueError, AttributeError), e:
                logging.error("unable to collect mc stats from %s : %s"
                              % (server, e))
                continue

            mc_server = Server(ip)

            # get bucket name from root and parent nodes
            bucket = DataHelper.get_bucket(root, parents)

            # initialize memcached source
            mc_source = MemcachedSource(mc_server, bucket)

            # initialize handlers to dump data json doc
            j_handler = JsonHandler()
            s_hanlder = SerieslyHandler(store)

            # collect data from source and emit to handlers
            mc_coll = MemcachedCollector([mc_source], [j_handler, s_hanlder])
            mc_coll.collect()
            mc_coll.emit()
            stats.put([mc_source.fast, mc_source.meta], block=True)
            stats.put([mc_source.slow, mc_source.meta], block=True)

        delta = time.time() - start
        logging.debug("collected mc stats from %s, took %s seconds"
                      % (val, delta))

        if delta < timeout:
            logging.debug("mc_worker sleep for %s seconds" % (timeout -delta))
            time.sleep(timeout - delta)

    logging.info("mc_worker stopped")
