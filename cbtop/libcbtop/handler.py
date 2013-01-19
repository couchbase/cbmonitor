#!/usr/bin/env python

class Handler(object):
    """
    Base class for data handlers
    """
    def handle(self, source):
        """
        Consume and handle a data source
        """
        raise NotImplementedError(
            "handle() has not been implemented")