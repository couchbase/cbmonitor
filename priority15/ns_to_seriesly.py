#!/usr/bin/env python
from optparse import OptionParser
import time
import sys

import requests
from seriesly import Seriesly

from cbm_metadata_client import MetadataClient


class SerieslyStore(object):

    def __init__(self, host, dbname):
        self.seriesly = Seriesly(host)
        if dbname not in self.seriesly.list_dbs():
            self.seriesly.create_db(dbname)
        self.dbname = dbname

    def append(self, data):
        self.seriesly[self.dbname].append(data)


class NSCollector(object):

    def __init__(self, host, cluster, store):
        self.store = store
        self.cluster = cluster
        self.root_url = "http://{0}:8091".format(host)

    def _get_nodes(self):
        pool = requests.get(self.root_url + "/pools/default").json()
        for node in pool["nodes"]:
            yield node["hostname"].split(":")[0]

    def _get_buckets(self):
        buckets = requests.get(self.root_url + "/pools/default/buckets").json()
        for bucket in buckets:
            yield bucket["name"], bucket["stats"]

    def _get_metrics(self):
        bucket, stats = self._get_buckets().next()
        stats = requests.get(self.root_url + stats["directoryURI"]).json()
        for block in stats["blocks"]:
            for metric in block["stats"]:
                yield metric["name"]

    def _last_stats(self, samples):
        return dict((k, v[-1]) for k, v in samples['op']['samples'].iteritems())

    def collect(self):
        for bucket, stats in self._get_buckets():
            uri = stats["uri"]
            samples = requests.get(self.root_url + uri).json()
            data = {
                "metric": {self.cluster: {bucket: self._last_stats(samples)}}
            }
            self.store.append(data)

            stats_list = requests.get(self.root_url + stats["nodeStatsListURI"]).json()
            for server in stats_list["servers"]:
                host = server["hostname"].split(":")[0]
                uri = server["stats"]["uri"]
                samples = requests.get(self.root_url + uri).json()
                data = {
                    "metric": {self.cluster: {bucket: {host: self._last_stats(samples)}}}
                }
                self.store.append(data)

    def update_metadata(self):
        mc = MetadataClient()
        mc.add_cluster(self.cluster)
        for bucket, _ in self._get_buckets():
            mc.add_bucket(self.cluster, bucket)
            for metric in self._get_metrics():
                mc.add_metric(self.cluster, metric, bucket)
            for node in self._get_nodes():
                mc.add_server(self.cluster, node)
                for metric in self._get_metrics():
                    mc.add_metric(self.cluster, metric, bucket, node)


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
                      help='database name', metavar='seriesly_db')

    options, args = parser.parse_args()

    if not options.database:
        parser.print_help()
        sys.exit()

    return options


def main():
    options = parse_args()

    store = SerieslyStore(options.out_host, options.database)

    ns_collector = NSCollector(options.node, options.cluster, store)

    ns_collector.update_metadata()
    while True:
        try:
            ns_collector.collect()
            time.sleep(options.interval)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
