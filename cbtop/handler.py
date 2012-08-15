#!/usr/bin/env python

class Handler:
    """
    Interface all data handlers should follow
    """
    def handle(self, source):
        """
        Consume and handle a data source
        """
        raise NotImplementedError(
            "handle() has not been implemented")