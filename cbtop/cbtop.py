#!/usr/bin/env python

import logging
import logging.config
import ConfigParser
import sys
import signal
from optparse import OptionParser

from libcbtop.main import main
import libcbtop.paint as pt

USAGE = """./%prog HOST [options]

Monitor a couchbase cluster.

Examples:
    ./%prog                     -- defaults to 127.0.0.1
    ./%prog 10.2.1.65
    ./%prog 10.2.1.65 -i 4"""

HOST = "127.0.0.1"
ctl = {}

try:
    logging.config.fileConfig("logging.conf")
except ConfigParser.NoSectionError:
    logging.config.fileConfig("cbtop/logging.conf")


def handle_signal(signum, frame):
    """
    Handles registered signals and exit.
    """
    logging.info("received signal %s, aborting" % signum)

    global ctl
    if not ctl["bg"]:
        pt.exit_fullscreen()

    ctl["run_ok"] = False


def usage():
    print USAGE
    sys.exit(-1)


def cbtop_main():
    signal.signal(signal.SIGINT, handle_signal)

    parser = OptionParser(usage=USAGE)
    parser.add_option("-i", "--itv", dest="itv", default="1",
                      help="stats polling interval (seconds)")
    parser.add_option("-d", "--dbhost", dest="dbhost", default=HOST,
                      help="host where seriesly database is located")
    parser.add_option("-s", "--dbslow", dest="dbslow", default="slow",
                      help="seriesly database to store slow changing data")
    parser.add_option("-f", "--dbfast", dest="dbfast", default="fast",
                      help="seriesly database to store fast changing data")
    parser.add_option("-b", "--background", dest="bg", default=False,
                      action="store_true", help="run cbtop in background")
    options, args = parser.parse_args()

    if len(args) > 0:
        _server = args[0]
    else:
        _server = HOST

    try:
        _itv = int(options.itv)
    except ValueError, e:
        logging.error("invalid polling interval: %s" % options.itv)
        usage()

    global ctl
    ctl = {"run_ok": True, "bg": options.bg}
    main(_server, itv=_itv, ctl=ctl, dbhost=options.dbhost,
         dbslow=options.dbslow, dbfast=options.dbfast)

if __name__ == "__main__":
    cbtop_main()
