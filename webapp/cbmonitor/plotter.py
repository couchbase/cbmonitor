import os
import re
from multiprocessing import Pool, cpu_count

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({'font.size': 5})
matplotlib.rcParams.update({'lines.linewidth': 1})
from matplotlib.pyplot import figure, grid

from eventlet import GreenPool
from reportlab.lib.pagesizes import landscape, B4
from reportlab.platypus import SimpleDocTemplate, Image
from seriesly import Seriesly
from seriesly.exceptions import NotExistingDatabase
from django.conf import settings

import models


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


class Plotter(object):

    def __init__(self):
        self.db = Seriesly()

        self.fig = figure()
        self.fig.set_size_inches(4.66, 2.625)

        self.urls = list()
        self.images = list()

        self.async_pool = GreenPool()
        self.mp_pool = Pool(cpu_count())

    def __del__(self):
        self.mp_pool.close()

    def _get_metrics(self):
        """Get all metrics object for given snapshot"""
        snapshot = models.Snapshot.objects.get(name=self.snapshot)
        return models.Observable.objects.filter(cluster=snapshot.cluster,
                                                type_id="metric").values()

    def _get_data(self, cluster, server, bucket, metric):
        """Query data using metric as key, server and bucket as filters"""
        query_params = {
            "group": 10000,  # 10 seconds
            "ptr": "/samples/{0}".format(metric),
            "reducer": 'avg',
            "f": ["/meta/server", "/meta/bucket"],
            "fv": [server or "none", bucket or "none"]
        }
        response = self.db[cluster].query(query_params)

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

    def _savePDF(self):
        """Save PNG charts as PDF report"""
        _, media_path = self._generate_PDF_meta()
        doc = SimpleDocTemplate(media_path, pagesize=landscape(B4))
        if not os.path.exists(media_path):
            pages = list()
            for filename in sorted(self.images):
                pages.append(Image(filename))
            doc.build(pages)

    def _extract(self, metric):
        """Extract time series data and metadata"""
        bucket = models.Bucket.objects.get(id=metric["bucket_id"])
        cluster = metric["cluster_id"]
        server = metric["server_id"]
        name = metric["name"]

        title, url, filename = \
            self._generate_PNG_meta(cluster, server, bucket, name)

        if os.path.exists(filename):
            self.urls.append([title, url])
            self.images.append(filename)
            return
        try:
            timestamps, values = self._get_data(cluster, server, bucket, name)
            if set(values) - set([None]):
                return timestamps, values, title, filename, url
        except NotExistingDatabase:
            return

    def pdf(self, snapshot):
        """"End point of PDF plotter"""
        self.plot(snapshot)
        self._savePDF()
        media_url, _ = self._generate_PDF_meta()
        return media_url

    def plot(self, snapshot):
        """"End point of PNG plotter"""
        self.snapshot = snapshot
        apply_results = list()
        for data in self.async_pool.imap(self._extract, self._get_metrics()):
            if data:
                apply_results.append(  # (timestamps, values, title, filename)
                    self.mp_pool.apply_async(savePNG, data[:4])
                )
                self.images.append(data[3])  # filename
                self.urls.append([data[2], data[4]])  # title, url
        for result in apply_results:
            result.get()
        return sorted(self.urls)
