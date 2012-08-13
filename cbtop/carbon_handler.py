#!/usr/bin/env python

import logging

from handler import Handler
from libcarbon.carbon_feeder import CarbonFeeder

class CarbonHandler(Handler):
    """
    Handler to dump data to carbon
    """
    def __init__(self, host):
        self.host = host    # hostname or ip of the carbon server

    def handle(self, data):
        """
        put data into carbon
        """
        if not data or not host:
            logging.error("unable to handle : invalid data or hostname")
            return False

        c_feeder = CarbonFeeder(self.host)
        if not c_feeder:
            logging.error("unable to create feeder")
            return False

        # unpack data and send to carbon
        # read the json metadata and send

