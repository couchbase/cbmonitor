#!/usr/bin/env python

class Collector:
    """
    collect data from data @class Source
    emit data to different types of data handlers
    """

    def collect(self):
        """
        collect data from data source.
        @return data been collected
        """
        raise NotImplementedError(
            "collect() has not been implemented")

    def process(self):
        """
        optionally process the data
        """
        raise NotImplementedError(
            "process() has not been implemented")

    def emit(self):
        """
        emit data to a data handler
        """
        raise NotImplementedError(
            "emit() has not been implemented")