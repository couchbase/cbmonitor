from optparse import OptionParser
import time
import sys

from stores.seriesly_store import SerieslyStore
from collectors.ns_server import NSServer


def parse_args():
    usage = "usage: %prog [options]\n\n" +\
            "Example: %prog -i 5 -c default -n 127.0.0.1 -s 127.0.0.1s -d cbmonitor"

    parser = OptionParser(usage)

    parser.add_option('-i', dest='interval', default=5, type="int",
                      help='polling interval', metavar=5)
    parser.add_option('-c', dest='cluster', default='default',
                      help='cluster name', metavar='default')
    parser.add_option('-n', dest='node', default='127.0.0.1',
                      help='node address', metavar='127.0.0.1')
    parser.add_option('-s', dest='out_host', default='127.0.0.1',
                      help='seriesly address', metavar='127.0.0.1')
    parser.add_option('-d', dest='database', default='cbmonitor',
                      help='database name', metavar='cbmonitor')

    options, args = parser.parse_args()

    if not options.database:
        parser.print_help()
        sys.exit()

    return options


def main():
    options = parse_args()

    store = SerieslyStore(options.out_host, options.database)

    ns_collector = NSServer(options.node, options.cluster, store)

    ns_collector.update_metadata()
    while True:
        try:
            ns_collector.collect()
            time.sleep(options.interval)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
