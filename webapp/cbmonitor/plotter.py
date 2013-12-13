import os
import re
from calendar import timegm
from collections import defaultdict
from itertools import cycle
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
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import seriesly
from cbagent.stores import SerieslyStore
from django.conf import settings
from eventlet import GreenPool
from scipy import stats

from cbmonitor import models
from cbmonitor.constants import (LABELS, PALETTE,
                                 HISTOGRAMS, ZOOM_HISTOGRAMS,
                                 NON_ZERO_VALUES,
                                 KDE,
                                 SMOOTH_SUBPLOTS,
                                 )


class Colors(object):

    def __init__(self):
        self.cycle = cycle(PALETTE)

    def next(self):
        return self.cycle.next()


# Defined externally in order to be pickled
def save_png(filename, series, ylabel, labels, chart_id, rebalances):
    fig = plt.figure(figsize=(4.66, 2.625))

    colors = Colors()

    ax = fig.add_subplot(1, 1, 1)
    ax.ticklabel_format(useOffset=False)

    if chart_id in ("_lt90", "_gt90", "_histo"):
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Percentile")
        width = cycle((0.6, 0.4))
        align = cycle(("edge", "center"))
        if chart_id == "_lt90":
            percentiles = range(1, 90)
            x = percentiles
            plt.xlim(0, 90)
        elif chart_id == "_gt90":
            percentiles = (90, 95, 97.5, 99, 99.9, 99.99, 99.999)
            x = range(len(percentiles))
            plt.xticks(x, percentiles)
        else:
            percentiles = range(1, 100)
            x = percentiles
            plt.xlim(0, 100)
        for i, s in enumerate(series):
            y = np.percentile(s.values, percentiles)
            ax.bar(x, y, linewidth=0.0, label=labels[i],
                   width=width.next(), align=align.next(), color=colors.next())
    elif chart_id == "_subplot":
        ax.set_ylabel(ylabel)
        map(lambda s: s.set_color('none'), ax.spines.values())
        ax.tick_params(top='off', bottom='off', left='off', right='off',
                       labelcolor='w')
        ax.grid(None)

        for i, s in enumerate(series):
            color = colors.next()

            ax = fig.add_subplot(2, 1, 1)
            ax.plot(s.index, s.values, label=labels[i], color=color)
            plt.setp(ax.get_xticklabels(), visible=False)
            ymin, ymax = ax.get_ylim()
            plt.ylim(ymin=0, ymax=max(1, ymax * 1.05))

            ax = fig.add_subplot(2, 1, 2)
            rolling_median = pd.rolling_median(s, window=5)
            ax.plot(s.index, rolling_median, label=labels[i], color=color)
            ax.set_xlabel("Time elapsed, sec")
            ymin, ymax = ax.get_ylim()
            plt.ylim(ymin=0, ymax=max(1, ymax * 1.05))
    elif chart_id == "_kde":
        ax.set_ylabel("Kernel density estimation")
        ax.set_xlabel(ylabel)
        for i, s in enumerate(series):
            x = np.linspace(0, int(s.quantile(0.99)), 200)
            kde = stats.kde.gaussian_kde(s.values)
            ax.plot(x, kde(x), label=labels[i], color=colors.next())
    else:
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Time elapsed, sec")
        for i, s in enumerate(series):
            ax.plot(s.index, s.values, label=labels[i], color=colors.next())
        ymin, ymax = ax.get_ylim()
        plt.ylim(ymin=0, ymax=max(1, ymax * 1.05))

        colors = Colors()
        for rebalance_start, rebalance_end in rebalances:
            plt.axvspan(rebalance_start, rebalance_end,
                        facecolor=colors.next(), alpha=0.1, linewidth=0.5)

    legend = ax.legend()
    legend.get_frame().set_linewidth(0.5)

    fig.tight_layout()
    fig.savefig(filename, dpi=200)
    plt.close()


class Plotter(object):

    def __init__(self):
        self.db = seriesly.Seriesly()
        self.all_dbs = self.db.list_dbs()

        self.urls = list()
        self.images = list()

        self.eventlet_pool = GreenPool()
        self.mp_pool = Pool(cpu_count())

    def __del__(self):
        self.mp_pool.close()

    def query_data(self, snapshot, cluster, server, bucket, metric, collector):
        query_params = {"ptr": "/{0}".format(metric), "reducer": "avg",
                        "group": 5000}
        if snapshot.name != "all_data":
            ts_from = timegm(snapshot.ts_from.timetuple()) * 1000
            ts_to = timegm(snapshot.ts_to.timetuple()) * 1000
            group = max((ts_from - ts_to) / 500, 5000)  # min 5s; max 500 points
            query_params.update({"group": group, "from": ts_from, "to": ts_to})
        db_name = SerieslyStore.build_dbname(cluster, server, bucket, collector)
        if db_name in self.all_dbs:
            try:
                return self.db[db_name].query(query_params)
            except seriesly.exceptions.ConnectionError:
                return
        else:
            return

    def generate_png_meta(self, snapshot, cluster, server, bucket, metric):
        metric = metric.replace("/", "_")
        title = "{0}] {1}".format(bucket, metric)  # [server bucket] metric
        if server:
            title = "[{0} {1}".format(server, title)
        else:
            title = "[" + title

        filename = "".join((snapshot.name, cluster, title))
        filename = re.sub(r"[\[\]/\\:\*\?\"<>\|& ]", "", filename)
        filename += "{suffix}.png"

        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return title, media_url, media_path

    def get_series(self, metric, data):
        data = dict((k, v[0]) for k, v in data.iteritems())
        series = pd.Series(data)
        series.index = series.index.astype("uint64")
        series.rename(lambda x: x - series.index.values.min(), inplace=True)
        series.rename(lambda x: x / 1000, inplace=True)  # ms -> s
        series.dropna()  # otherwise it may break kde

        if metric in NON_ZERO_VALUES and (series == 0).all():
            return None
        else:
            return series

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
            data = self.query_data(snapshot, cluster, server, bucket, name,
                                   collector)
            if data:
                series = self.get_series(metric=name, data=data)
                if series is not None:
                    merge["series"].append(series)
                    if snapshot.name == "all_data":
                        merge["labels"].append(cluster)
                    else:
                        merge["labels"].append(snapshot.name)
            merge_cluster += cluster
        title, url, filename = self.generate_png_meta(snapshot, merge_cluster,
                                                      server, bucket, name)

        return merge["series"], merge["labels"], title, filename, url

    def detect_rebalance(self, observables):
        rebalances = []
        if observables[0][0].name == "rebalance_progress":
            series, _, _, _, _ = self.extract(observables)
            for s in series:
                s = s.dropna()
                rebalance = s[s > 0]
                rebalances.append((rebalance.index[0], rebalance.index[-1]))
        return rebalances

    def plot(self, metrics):
        apply_results = list()
        metrics = tuple(metrics)
        rebalances = self.detect_rebalance(metrics[0])

        for data in self.eventlet_pool.imap(self.extract, metrics):
            series, labels, title, filename, url = data
            metric = title.split()[-1]
            if series:
                ylabel = LABELS.get(metric, metric)

                chart_ids = [""]
                if metric in HISTOGRAMS:
                    chart_ids += ["_histo"]
                if metric in ZOOM_HISTOGRAMS:
                    chart_ids += ["_lt90", "_gt90"]
                if metric in KDE:
                    chart_ids += ["_kde"]
                if metric in SMOOTH_SUBPLOTS:
                    chart_ids[0] = "_subplot"

                if not os.path.exists(filename):
                    for chart_id in chart_ids:
                        apply_results.append(self.mp_pool.apply_async(
                            save_png,
                            args=(filename.format(suffix=chart_id),
                                  series, ylabel, labels, chart_id, rebalances)
                        ))
                for chart_id in chart_ids:
                    self.urls.append([title, url.format(suffix=chart_id)])
                    self.images.append(filename.format(suffix=chart_id))
        for result in apply_results:
            result.get()
