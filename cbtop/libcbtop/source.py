#!/usr/bin/env python

class Source(object):
    """
    Base class for all data sources
    """
    def connect(self):
        """
        Connect to the upstream data provider
        """
        raise NotImplementedError(
            "connect() has not been implemented")

    def feed(self):
        """
        Feed downstream pipe with data
        """
        raise NotImplementedError(
            "feed() has not been implemented")

    def disconnect(self):
        """
        Disconnect from the upstream data provider
        """
        raise NotImplementedError(
            "disconnect() has not been implemented")