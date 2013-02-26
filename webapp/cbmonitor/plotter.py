import os

import matplotlib
matplotlib.use('Agg')
from matplotlib.pyplot import figure, grid
from seriesly import Seriesly
from seriesly.exceptions import NotExistingDatabase
from django.conf import settings

import models


class Plotter(object):

    def __init__(self):
        self.db = Seriesly()
        self.fig = figure()

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

    def _generate_filename(self, cluster, server, bucket, metric):
        """Generate filename in webapp media folder"""
        filename = "_".join((cluster, str(server), str(bucket),
                             metric.replace("/", "_")))
        return os.path.join(settings.MEDIA_ROOT, filename + ".png")

    def _savePNG(self, timestamps, values, metric, filename):
        """Save chart as PNG file"""
        self.fig.clear()

        ax = self.fig.add_subplot(1, 1, 1)
        ax.set_title(metric)
        ax.set_xlabel("Time elapsed (sec)")
        grid()
        ax.plot(timestamps, values, '.')

        self.fig.savefig(filename)

    def plot(self, snapshot):
        for metric in self._get_metrics(snapshot):
            bucket = models.Bucket.objects.get(id=metric["bucket_id"])
            cluster = metric["cluster_id"]
            server = metric["server_id"]
            name = metric["name"]

            try:
                timestamps, values = self._get_data(cluster, server, bucket,
                                                    name)
            except NotExistingDatabase:
                continue
            filename = self._generate_filename(cluster, server, bucket, name)

            self._savePNG(timestamps, values, name, filename)
        return []
