#!/usr/bin/env python

import logging
import sys

try:
    from blessings import Terminal
except ImportError:
    print "cbtop requires blessings package to run"
    print "check out http://pypi.python.org/pypi/blessings/"
    sys.exit(-1)

class BLSConstant:
    """
    Wrapper to store constant mappings
    """
    COLOR = {"black": 0,
             "red": 1,
             "green": 2,
             "yellow": 3,
             "blue": 4,
             "magenta": 5,
             "cyan": 6,
             "white": 7}

    TF = {True: COLOR["green"],
          False: COLOR["red"]}

    STATUS = {"healthy": COLOR["green"],
              "unhealthy": COLOR["red"]}

class BLSHelper:
    """
    Helper class to refresh terminal screen,
    using blessings package

    http://pypi.python.org/pypi/blessings
    """
    _TERM = Terminal()
    _SERVERS = set()         # [server ips]

    @staticmethod
    def show_carbon(carbon):
        """Print out carbon server address"""
        with BLSHelper._TERM.location(0, 1):
            print BLSHelper._TERM.bold("carbon: %s" %carbon)

    @staticmethod
    def add_server(server):
        """Add server to the target server list"""
        BLSHelper._SERVERS.add(server)
        BLSHelper._show_servers()

    @staticmethod
    def del_server(server):
        """Del server from the target server list"""
        try:
            BLSHelper._SERVERS.remove(server)
            BLSHelper._show_servers()
        except:
            logging.error("server not exist: %s" % server)

    @staticmethod
    def _show_servers():
        """
        Print out the server list
        Call add_server() or del_server() to show server list
        """
        with BLSHelper._TERM.location(0, 2):
            print "servers: (%d)" % len(BLSHelper._SERVERS)
            for server in BLSHelper._SERVERS:
                print server

    @staticmethod
    def show_status(status):
        """Print out status of the cluster"""
        color = BLSConstant.STATUS.get(
            status, BLSConstant.COLOR["blue"])

        with BLSHelper._TERM.location(30, 2):
            print BLSHelper._TERM.color(color)("[" + status + "]")

    @staticmethod
    def show_balanced(tf):
        """Print out balanced info"""
        color = BLSConstant.TF.get(
            tf, BLSConstant.COLOR["blue"])

        if tf:
            status = "balanced"
        else:
            status = "unbalanced"

        with BLSHelper._TERM.location(40, 2):
            print BLSHelper._TERM.color(color)("[" + status + "]")

    @staticmethod
    def enter_fullscreen():
        """
        Invoke before printing out anything.
        This method should be replaced by or merged to blessings package
        """
        BLSHelper._TERM.stream.write(
            BLSHelper._TERM.enter_fullscreen)

    @staticmethod
    def exit_fullscreen():
        """
        Invoke before printing out anything.
        This method should be replaced by or merged to blessings package
        """
        BLSHelper._TERM.stream.write(
            BLSHelper._TERM.exit_fullscreen)