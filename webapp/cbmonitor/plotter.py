import os

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({'font.size': 5})
matplotlib.rcParams.update({'lines.linewidth': 1})
from matplotlib.pyplot import figure, grid

from reportlab.lib.pagesizes import landscape, B4
from reportlab.platypus import SimpleDocTemplate, Image
from seriesly import Seriesly
from seriesly.exceptions import NotExistingDatabase
from django.conf import settings

import models


class Plotter(object):

    def __init__(self):
        self.db = Seriesly()
        self.fig = figure()
        self.fig.set_size_inches(4.66, 2.625)

    def _get_metrics(self, snapshot):
        """Get all metrics object for given snapshot"""
        snapshot = models.Snapshot.objects.get(name=snapshot)
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
        title = "_".join((cluster, str(server), str(bucket), metric))
        filename = title + ".png"
        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return title, media_url, media_path

    def _generate_PDF_meta(self, snapshot):
        """Generate PDF metadata (filenames, URLs)"""
        filename = snapshot + ".pdf"
        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return media_url, media_path

    def _savePNG(self, timestamps, values, title, filename):
        """Save chart as PNG file"""
        self.fig.clear()

        ax = self.fig.add_subplot(1, 1, 1)
        ax.set_title(title)
        ax.set_xlabel("Time elapsed (sec)")
        grid()
        ax.plot(timestamps, values, '.', markersize=3)

        self.fig.savefig(filename, dpi=200)

    def _savePDF(self, snapshot, images):
        """Save PNG charts as PDF report"""
        _, media_path = self._generate_PDF_meta(snapshot)
        doc = SimpleDocTemplate(media_path, pagesize=landscape(B4))
        if not os.path.exists(media_path):
            pages = list()
            for filename in sorted(images):
                pages.append(Image(filename))
            doc.build(pages)

    def pdf(self, snapshot):
        """"End point of PDF plotter"""
        self.plot(snapshot)
        media_url, _ = self._generate_PDF_meta(snapshot)
        return media_url

    def plot(self, snapshot):
        """"End point of PNG plotter"""
        urls = list()
        images = list()
        for metric in self._get_metrics(snapshot):
            bucket = models.Bucket.objects.get(id=metric["bucket_id"])
            cluster = metric["cluster_id"]
            server = metric["server_id"]
            name = metric["name"]
            title, url, filename = \
                self._generate_PNG_meta(cluster, server, bucket, name)
            if os.path.exists(filename):
                urls.append([title, url])
                images.append(filename)
                continue
            try:
                timestamps, values = self._get_data(cluster, server, bucket,
                                                    name)
            except NotExistingDatabase:
                continue
            else:
                if set(values) - set([None]):
                    self._savePNG(timestamps, values, title, filename)
                    images.append(filename)
                    urls.append([title, url])
        self._savePDF(snapshot, images)
        return sorted(urls)
