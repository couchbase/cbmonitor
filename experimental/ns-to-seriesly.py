#!/usr/bin/env python
from optparse import OptionParser
import time
import sys

import requests
from seriesly import Seriesly


class NsToSeriesly(object):

    def __init__(self, in_host, out_host, database):
        self.url = 'http://{0}:8091/'.format(in_host) + \
            'pools/default/buckets/default/stats?zoom=minute'

        self.database = database
        self.seriesly = Seriesly(host=out_host)
        if database not in self.seriesly.list_dbs():
            self.seriesly.create_db(database)

    def collect(self):
        r = requests.get(self.url)

        all_stats = r.json['op']['samples']
        last_stats = dict((k, v[-1]) for k, v in all_stats.iteritems())

        self.store(last_stats)

    def store(self, data):
        self.seriesly[self.database].append(data)


def parse_args():
    usage = "usage: %prog [options]\n\n" +\
            "Example: %prog -i 127.0.0.1 -o 127.0.0.1 -d ns_db "

    parser = OptionParser(usage)

    parser.add_option('-i', dest='in_host', default='127.0.0.1',
                      help='input address', metavar='127.0.0.1')
    parser.add_option('-o', dest='out_host', default='127.0.0.1',
                      help='output address', metavar='127.0.0.1')
    parser.add_option('-d', dest='database',
                      help='database name', metavar='seriesly_db')

    options, args = parser.parse_args()

    if not options.database:
        parser.print_help()
        sys.exit()

    return options


def main():
    options = parse_args()

    n2s = NsToSeriesly(in_host=options.in_host,
                       out_host=options.out_host,
                       database=options.database)
    while True:
        try:
            print "Collecting and storing data"
            n2s.collect()
            time.sleep(5)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
