import os
import re
from calendar import timegm
from multiprocessing import Pool, cpu_count

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({'font.size': 5})
matplotlib.rcParams.update({'lines.linewidth': 1})
from matplotlib.pyplot import figure, grid, close

from cbagent.stores import SerieslyStore
from django.conf import settings
from eventlet import GreenPool
from reportlab.lib.pagesizes import landscape, B4
from reportlab.platypus import SimpleDocTemplate, Image
from seriesly import Seriesly
from seriesly.exceptions import NotExistingDatabase

from cbmonitor import models


# Defined externally in order to be pickled
def savePNG(timestamps, values, filename):
    fig = figure()
    fig.set_size_inches(4.66, 2.625)

    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel("Time elapsed (sec)")
    grid()
    ax.plot(timestamps, values, '.', markersize=3)

    fig.savefig(filename, dpi=200)
    close()


class Plotter(object):

    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.db = Seriesly()

        self.urls = list()
        self.images = list()

        self.eventlet_pool = GreenPool()
        self.mp_pool = Pool(cpu_count())

    def __del__(self):
        self.mp_pool.close()

    def _get_data(self, cluster, server, bucket, metric, collector):
        # Query data using metric as key
        ts_from = timegm(self.snapshot.ts_from.timetuple()) * 1000
        ts_to = timegm(self.snapshot.ts_to.timetuple()) * 1000
        group = max((ts_from - ts_to) / 500, 5000)  # min 5 sec; max 500 points
        query_params = {
            "ptr": "/{0}".format(metric), "reducer": "avg",
            "group": group, "from": ts_from, "to": ts_to
        }
        db_name = SerieslyStore.build_dbname(cluster, server, bucket, collector)
        response = self.db[db_name].query(query_params)

        # Convert data and generate sorted lists of timestamps and values
        timestamps = list()
        values = list()
        data = dict((k, v[0]) for k, v in response.iteritems())
        for timestamp, value in sorted(data.iteritems()):
            timestamps.append(int(timestamp))
            values.append(value)

        # Substract first timestamp; convert to seconds
        timestamps = [(key - timestamps[0]) / 1000 for key in timestamps]

        return timestamps, values

    def _generate_PNG_meta(self, cluster, server, bucket, metric):
        metric = metric.replace("/", "_")
        title = "{0}] {1}".format(bucket, metric)  # [server bucket] metric
        if server:
            title = "[{0} {1}".format(server, title)
        else:
            title = "[" + title

        filename = "".join((self.snapshot.name, cluster, title))
        filename = re.sub(r"[\[\]/\\:\*\?\"<>\|& ]", "", filename)
        filename += ".png"

        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return title, media_url, media_path

    def _generate_PDF_meta(self):
        filename = self.snapshot.name + ".pdf"
        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return media_url, media_path

    def _savePDF(self, media_path):
        pages = [Image(filename) for filename in sorted(self.images)]
        doc = SimpleDocTemplate(media_path, pagesize=landscape(B4))
        doc.build(pages)

    def _extract(self, metric):
        """Extract time series data and metadata"""
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

        title, url, filename = \
            self._generate_PNG_meta(cluster, server, bucket, name)

        if os.path.exists(filename):
            self.urls.append([title, url])
            self.images.append(filename)
            return
        try:
            timestamps, values = self._get_data(cluster, server, bucket, name,
                                                collector)
            if set(values) - set([None]):
                return timestamps, values, title, filename, url
        except NotExistingDatabase:
            return

    def pdf(self, metrics):
        media_url, media_path = self._generate_PDF_meta()
        if not os.path.exists(media_path):
            self.plot(metrics)
            self._savePDF(media_path)
        return media_url

    def plot(self, metrics):
        apply_results = list()
        for data in self.eventlet_pool.imap(self._extract, metrics):
            if data:
                timestamps, values, title, filename, url = data
                apply_results.append(self.mp_pool.apply_async(
                    savePNG, args=(timestamps, values, filename)
                ))
                self.images.append(filename)
                self.urls.append([title, url])
        for result in apply_results:
            result.get()
