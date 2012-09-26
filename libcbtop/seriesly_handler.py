#!/usr/bin/env python

import logging
from handler import Handler

class SerieslyHandler(Handler):
    """
    Handler to dump data to seriesly
    """
    def __init__(self, store):
        self.store = store

    def handle(self, source):
        if not source:
            logging.error("unable to handle : invalid source")
            return False

        self.store.clear()
        if source.fast:
            self.store.fast = source.fast

        if source.slow:
            self.store.slow = source.slow
        self.store.persist()

        return True