#!/usr/bin/env python

class DataHelper:
    """
    Helper to retrieve data from particular nodes
    """
    @staticmethod
    def get_bucket(root, parents):
        """Get bucket name from root and parent nodes"""
        path = root.get("path", "")
        if path:
            # assume path like /pools/default
            return path.split("/")[-1]
        else:
            return "default"

    @staticmethod
    def get_ip(root, parent):
        """
        Get hostname or ip address from root and parent nodes

        Carbon needs to know the originator of the fast changing data, \
        for the purpose of contruct the metric info.
        """
        return root.get("host", "127.0.0.1")