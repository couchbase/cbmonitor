#!/usr/bin/env python

import logging
import logging.config
import ConfigParser
import signal
from optparse import OptionParser

from libcbtop.main import main
import libcbtop.paint as pt


DEFAULT_HOST = "127.0.0.1"
ctl = {}

try:
    logging.config.fileConfig("logging.conf")
except ConfigParser.NoSectionError:
    logging.config.fileConfig("cbtop/logging.conf")


def handle_signal(signum, frame):
    """Handles registered signals and exit."""
    global ctl

    logging.info("received signal %s, aborting" % signum)

    if not ctl["bg"]:
        pt.exit_fullscreen()

    ctl["run_ok"] = False


def parse_args():
    usage = \
        "./%prog HOST [options]\n\n" + \
        "Monitor a couchbase cluster.\n\n" + \
        "Examples:\n" + \
        "    ./%prog                     -- defaults to 127.0.0.1\n" + \
        "    ./%prog 10.2.1.65\n" + \
        "    ./%prog 10.2.1.65 -i 4\n"

    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--itv", dest="itv", default="1", type="int",
                      help="stats polling interval (seconds)")
    parser.add_option("-d", "--dbhost", dest="dbhost", default=DEFAULT_HOST,
                      help="host where seriesly database is located")
    parser.add_option("-s", "--dbslow", dest="dbslow", default="slow",
                      help="seriesly database to store slow changing data")
    parser.add_option("-f", "--dbfast", dest="dbfast", default="fast",
                      help="seriesly database to store fast changing data")
    parser.add_option("-b", "--background", dest="bg", default=False,
                      action="store_true", help="run cbtop in background")
    return parser.parse_args()


def cbtop_main():
    global ctl

    signal.signal(signal.SIGINT, handle_signal)

    options, args = parse_args()
    server = args and args[0] or DEFAULT_HOST
    ctl = {"run_ok": True, "bg": options.bg}

    main(server, itv=options.itv, ctl=ctl, dbhost=options.dbhost,
         dbslow=options.dbslow, dbfast=options.dbfast)

if __name__ == "__main__":
    cbtop_main()
