#!/usr/bin/env python

class Handler:
    """
    interface all data handlers should follow
    """
    def handle(self, data):
        """
        consume and handle data
        """
        raise NotImplementedError(
            "handle() has not been implemented")