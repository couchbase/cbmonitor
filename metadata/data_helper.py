#!/usr/bin/env python

class DataHelper:
    """
    Helper to retrieve data from particular nodes
    """
    @staticmethod
    def get_bucket(root, parents):
        """Get bucket name from root and parent nodes"""
        #TODO
        return "default"

    @staticmethod
    def get_ip(root, parent):
        """
        Get hostname or ip address from root and parent nodes

        Carbon needs to know the originator of the fast changing data, \
        for the purpose of contruct the metric info.
        """
        #TODO
        return "127.0.0.1"