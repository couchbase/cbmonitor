import os
import re
from multiprocessing import Pool, cpu_count

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({'font.size': 5})
matplotlib.rcParams.update({'lines.linewidth': 1})
from matplotlib.pyplot import figure, grid, close

from cbagent.stores.seriesly_store import SerieslyStore
from eventlet import GreenPool
from reportlab.lib.pagesizes import landscape, B4
from reportlab.platypus import SimpleDocTemplate, Image
from seriesly import Seriesly
from seriesly.exceptions import NotExistingDatabase
from django.conf import settings

from cbmonitor import models


def savePNG(timestamps, values, title, filename):
    """Save chart as PNG file. Defined externally in order to be pickled"""
    fig = figure()
    fig.set_size_inches(4.66, 2.625)

    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(title)
    ax.set_xlabel("Time elapsed (sec)")
    grid()
    ax.plot(timestamps, values, '.', markersize=3)

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

    def _get_metrics(self):
        """Get all metrics object for given snapshot"""
        snapshot = models.Snapshot.objects.get(name=self.snapshot)
        return models.Observable.objects.filter(cluster=snapshot.cluster,
                                                type_id="metric").values()

    def _get_data(self, cluster, server, bucket, metric, collector):
        """Query data using metric as key, server and bucket as filters"""
        query_params = {
            "group": 10000,  # 10 seconds
            "ptr": "/{0}".format(metric), "reducer": "avg"
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
        """Generate PNG metadata (filenames, URLs)"""
        metric = metric.replace("/", "_")
        title = "{0}] {1}".format(bucket, metric)  # [server bucket] metric
        if server:
            title = "[{0} {1}".format(server, title)
        else:
            title = "[" + title

        filename = "".join((self.snapshot, cluster, title))
        filename = re.sub(r"[\[\]/\\:\*\?\"<>\|& ]", "", filename)
        filename += ".png"

        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return title, media_url, media_path

    def _generate_PDF_meta(self):
        """Generate PDF metadata (filenames, URLs)"""
        filename = self.snapshot + ".pdf"
        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return media_url, media_path

    def _savePDF(self, media_path):
        """Save PNG charts as PDF report"""
        pages = [Image(filename) for filename in sorted(self.images)]
        doc = SimpleDocTemplate(media_path, pagesize=landscape(B4))
        doc.build(pages)

    def _extract(self, metric):
        """Extract time series data and metadata"""
        bucket = str(models.Bucket.objects.get(id=metric["bucket_id"]))
        cluster = metric["cluster_id"]
        server = metric["server_id"]
        name = metric["name"]
        collector = metric["collector"]

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

    def pdf(self, snapshot):
        """"End point of PDF plotter"""
        self.snapshot = snapshot
        media_url, media_path = self._generate_PDF_meta()
        if not os.path.exists(media_path):
            self.plot()
            self._savePDF(media_path)
        return media_url

    def plot(self, snapshot=None):
        """"End point of PNG plotter"""
        self.snapshot = snapshot or self.snapshot

        apply_results = list()
        for data in self.eventlet_pool.imap(self._extract, self._get_metrics()):
            if data:
                timestamps, values, title, filename, url = data
                result = self.mp_pool.apply_async(savePNG, data[:4])
                apply_results.append(result)
                self.images.append(filename)
                self.urls.append([title, url])

        for result in apply_results:
            result.get()

        return sorted(self.urls)
