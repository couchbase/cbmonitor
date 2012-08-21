#!/usr/bin/env python

class Collector(object):
    """
    Collector to collect data from data @class Source
    Emit data to different types of data handlers
    """
    def collect(self):
        """
        Collect data from data sources
        """
        raise NotImplementedError(
            "collect() has not been implemented")

    def process(self):
        """
        Optionally process the data
        """
        raise NotImplementedError(
            "process() has not been implemented")

    def emit(self):
        """
        Emit data to data handlers
        """
        raise NotImplementedError(
            "emit() has not been implemented")