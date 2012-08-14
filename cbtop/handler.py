#!/usr/bin/env python

class Handler:
    """
    interface all data handlers should follow
    """
    def handle(self, source):
        """
        consume and handle data source
        """
        raise NotImplementedError(
            "handle() has not been implemented")