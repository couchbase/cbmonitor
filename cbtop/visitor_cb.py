#!/usr/bin/env python

import logging
from sys_helper import is_num

from libcarbon.carbon_key import CarbonKey

class VisitorCallback:
    """
    Callbacks for metadata visitor
    """
    C_FEEDER = None        # @class CarbonFeeder

    @staticmethod
    def store_fast(root, parents, data, meta, coll,
                   key, val, meta_val, meta_inf, level):
        """Store time-series data into fast-changing database"""
        if not VisitorCallback.C_FEEDER:
            logging.error(
                "unable to store fast changing data : invalid CarbonFeeder")
            return False

        if is_num(val):
            c_key = CarbonKey("ns", "127.0.0.1", key)
            VisitorCallback.C_FEEDER.feed(c_key, val)

        return True

    @staticmethod
    def store_slow(root, parents, data, meta, coll,
                   key, val, meta_val, meta_inf, level):
        """Store time-series data into slow-changing database"""
        return True
