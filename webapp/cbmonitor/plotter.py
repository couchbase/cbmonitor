import os
import re
from calendar import timegm
from collections import defaultdict
from multiprocessing import Pool, cpu_count

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams.update({"font.size": 5})
matplotlib.rcParams.update({"lines.linewidth": 0.5})
matplotlib.rcParams.update({"lines.marker": "."})
matplotlib.rcParams.update({"lines.markersize": 3})
matplotlib.rcParams.update({"lines.linestyle": 'None'})
matplotlib.rcParams.update({"axes.linewidth": 0.5})
matplotlib.rcParams.update({"axes.grid": True})
matplotlib.rcParams.update({"axes.formatter.limits": (-6, 6)})
matplotlib.rcParams.update({"legend.numpoints": 1})
matplotlib.rcParams.update({"legend.fancybox": True})
matplotlib.rcParams.update({"legend.markerscale": 1.5})
matplotlib.rcParams.update({"legend.loc": 0})
matplotlib.rcParams.update({"legend.frameon": True})
from matplotlib.pyplot import figure, close, ylim

from cbagent.stores import SerieslyStore
from django.conf import settings
from eventlet import GreenPool
from seriesly import Seriesly
from seriesly.exceptions import NotExistingDatabase

from cbmonitor import models


# Defined externally in order to be pickled
def savePNG(filename, timestamps, values, labels):
    fig = figure()
    fig.set_size_inches(4.66, 2.625)

    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel("Time elapsed (sec)")
    ax.ticklabel_format(useOffset=False)
    for i in range(len(timestamps)):
        ax.plot(timestamps[i], values[i], label=labels[i])
    legend = ax.legend()
    legend.get_frame().set_linewidth(0.5)
    ymin, ymax = ax.get_ylim()
    ylim(ymin=0, ymax=max(1, ymax * 1.05))

    fig.savefig(filename, dpi=200)
    close()


class Plotter(object):

    def __init__(self):
        self.db = Seriesly()

        self.urls = list()
        self.images = list()

        self.eventlet_pool = GreenPool()
        self.mp_pool = Pool(cpu_count())

    def __del__(self):
        self.mp_pool.close()

    def get_data(self, snapshot, cluster, server, bucket, metric, collector):
        # Query data using metric as key
        query_params = {"ptr": "/{0}".format(metric), "reducer": "avg",
                        "group": 5000}
        if snapshot.name != "all_data":
            ts_from = timegm(snapshot.ts_from.timetuple()) * 1000
            ts_to = timegm(snapshot.ts_to.timetuple()) * 1000
            group = max((ts_from - ts_to) / 500, 5000)  # min 5 sec; max 500 points
            query_params.update({"group": group, "from": ts_from, "to": ts_to})
        db_name = SerieslyStore.build_dbname(cluster, server, bucket, collector)
        try:
            response = self.db[db_name].query(query_params)
        except NotExistingDatabase:
            return None, None

        # Convert data and generate sorted lists of timestamps and values
        timestamps = list()
        values = list()
        data = dict((k, v[0]) for k, v in response.iteritems())
        for timestamp, value in sorted(data.iteritems()):
            timestamps.append(int(timestamp))
            values.append(value)

        # Substract first timestamp; convert to seconds
        timestamps = [(key - timestamps[0]) / 1000 for key in timestamps]

        if set(values) - set([None]):
            return timestamps, values
        else:
            return None, None

    def generate_PNG_meta(self, snapshot, cluster, server, bucket, metric):
        metric = metric.replace("/", "_")
        title = "{0}] {1}".format(bucket, metric)  # [server bucket] metric
        if server:
            title = "[{0} {1}".format(server, title)
        else:
            title = "[" + title

        filename = "".join((snapshot.name, cluster, title))
        filename = re.sub(r"[\[\]/\\:\*\?\"<>\|& ]", "", filename)
        filename += ".png"

        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return title, media_url, media_path

    def extract_meta(self, metric):
        if metric.bucket_id:
            bucket = str(models.Bucket.objects.get(id=metric.bucket_id))
        else:
            bucket = ""
        if metric.server_id:
            server = str(models.Server.objects.get(id=metric.server_id))
        else:
            server = ""
        cluster = metric.cluster_id
        name = metric.name
        collector = metric.collector

        return cluster, server, bucket, name, collector

    def extract(self, meta):
        merge = defaultdict(list)
        merge_cluster = server = bucket = name = snapshot = ""
        for sub_metric, snapshot in meta:
            cluster, server, bucket, name, collector = self.extract_meta(
                sub_metric)
            timestamps, values = self.get_data(snapshot, cluster, server,
                                               bucket, name, collector)
            if timestamps and values:
                merge["timestamps"].append(timestamps)
                merge["values"].append(values)
                if snapshot.name == "all_data":
                    merge["labels"].append(cluster)
                else:
                    merge["labels"].append(snapshot.name)
            merge_cluster += cluster
        title, url, filename = self.generate_PNG_meta(snapshot, merge_cluster,
                                                      server, bucket, name)

        return merge["timestamps"], merge["values"], merge["labels"],\
            title, filename, url

    def plot(self, metrics):
        apply_results = list()
        for data in self.eventlet_pool.imap(self.extract, metrics):
            timestamps, values, labels, title, filename, url = data
            if timestamps and values:
                if not os.path.exists(filename):
                    apply_results.append(self.mp_pool.apply_async(
                        savePNG, args=(filename, timestamps, values, labels)
                    ))
                self.urls.append([title, url])
                self.images.append(filename)
        for result in apply_results:
            result.get()
