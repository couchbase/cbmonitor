#!/usr/bin/env python

class Source:
    """
    interface all data sources should follow.
    """
    def connect(self):
        """
        connect to the upstream data provider
        """
        raise NotImplementedError(
            "connect() has not been implemented")

    def feed(self):
        """
        feed downstream pipe with data
        """
        raise NotImplementedError(
            "feed() has not been implemented")

    def disconnect(self):
        """
        disconnect from the upstream data provider
        """
        raise NotImplementedError(
            "disconnect() has not been implemented")