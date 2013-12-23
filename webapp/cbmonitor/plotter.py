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
from django.conf import settings
from eventlet import GreenPool
from scipy import stats

from cbmonitor import constants


class Colors(object):

    def __init__(self):
        self.cycle = cycle(constants.PALETTE)

    def next(self):
        return self.cycle.next()


# Defined externally in order to be pickled
def init_ax(fig, dim=(1, 1, 1)):
    ax = fig.add_subplot(*dim)
    ax.ticklabel_format(useOffset=False)
    return ax


def plot_time_series(ax, series, labels, ylabel=None):
    colors = Colors()
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.set_xlabel("Time elapsed, sec")
    for i, s in enumerate(series):
        ax.plot(s.index, s, label=labels[i], color=colors.next())
    ymin, ymax = ax.get_ylim()
    plt.ylim(ymin=0, ymax=max(1, ymax * 1.05))


def plot_percentiles(ax, series, labels, ylabel, chart_id):
    colors = Colors()
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
        y = np.percentile(s, percentiles)
        ax.bar(x, y, linewidth=0.0, label=labels[i],
               width=width.next(), align=align.next(), color=colors.next())


def plot_score(ax, series, labels, ylabel):
    colors = Colors()
    ax.set_ylabel("Percentile of score ({})".format(ylabel))
    ax.set_xlabel("Time elapsed, sec")
    for i, s in enumerate(series):
        scoref = lambda x: stats.percentileofscore(x, s.quantile(0.9))
        rolling_score = pd.rolling_apply(s, min(len(s) / 15, 40), scoref)
        ax.plot(s.index, rolling_score, label=labels[i],
                color=colors.next())
        plt.ylim(ymin=0, ymax=105)


def plot_kde(ax, series, labels, ylabel):
    colors = Colors()
    ax.set_ylabel("Kernel density estimation")
    ax.set_xlabel(ylabel)
    for i, s in enumerate(series):
        x = np.linspace(0, int(s.quantile(0.99)), 200)
        kde = stats.kde.gaussian_kde(s)
        ax.plot(x, kde(x), label=labels[i], color=colors.next())


def plot_subplot_frame(ax, ylabel):
    ax.set_ylabel(ylabel)
    map(lambda s: s.set_color('none'), ax.spines.values())
    ax.tick_params(top='off', bottom='off', left='off', right='off',
                   labelcolor='w')
    ax.grid(None)


def plot_rolling_subplot(ax, series, labels):
    colors = Colors()
    for i, s in enumerate(series):
        rolling_median = pd.rolling_median(s, window=5)
        ax.plot(s.index, rolling_median, label=labels[i], color=colors.next())
        ymin, ymax = ax.get_ylim()
        plt.ylim(ymin=0, ymax=max(1, ymax * 1.05))


def highlight_rebalance(rebalances):
    colors = Colors()
    for rebalance_start, rebalance_end in rebalances:
        plt.axvspan(rebalance_start, rebalance_end,
                    facecolor=colors.next(), alpha=0.1, linewidth=0.5)


def plot_as_png(filename, series, labels, ylabel, chart_id, rebalances):
    fig = plt.figure(figsize=(4.66, 2.625))
    ax = init_ax(fig)

    if chart_id in ("_lt90", "_gt90", "_histo"):
        plot_percentiles(ax, series, labels, ylabel, chart_id)
    elif chart_id == "_subplot":
        plot_subplot_frame(ax, ylabel)

        ax = init_ax(fig, dim=(2, 1, 1))
        plot_rolling_subplot(ax, series, labels)
        highlight_rebalance(rebalances)

        ax = init_ax(fig, dim=(2, 1, 2))
        plot_time_series(ax, series, labels, ylabel=None)
        highlight_rebalance(rebalances)
    elif chart_id == "_kde":
        plot_kde(ax, series, labels, ylabel)
    elif chart_id == "_score":
        plot_score(ax, series, labels, ylabel)
        highlight_rebalance(rebalances)
    else:
        plot_time_series(ax, series, labels, ylabel)
        highlight_rebalance(rebalances)

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

    @staticmethod
    def build_dbname(cluster, server, bucket, collector):
        db_name = (collector or "") + cluster + (bucket or "") + (server or "")
        for char in "[]/\;.,><&*:%=+@!#^()|?^'\"":
            db_name = db_name.replace(char, "")
        return db_name

    def query_data(self, snapshot, cluster, server, bucket, metric, collector):
        query_params = {"ptr": "/{}".format(metric), "reducer": "avg",
                        "group": 5000}
        if snapshot.name != "all_data":
            ts_from = timegm(snapshot.ts_from.timetuple()) * 1000
            ts_to = timegm(snapshot.ts_to.timetuple()) * 1000
            group = max((ts_from - ts_to) / 500, 5000)  # min 5s; max 500 points
            query_params.update({"group": group, "from": ts_from, "to": ts_to})
        db_name = self.build_dbname(cluster, server, bucket, collector)
        if db_name in self.all_dbs:
            try:
                return self.db[db_name].query(query_params)
            except seriesly.exceptions.ConnectionError:
                return
        else:
            return

    def generate_png_meta(self, snapshot, cluster, server, bucket, metric):
        metric = metric.replace("/", "_")
        title = "{}] {}".format(bucket, metric)  # [server bucket] metric
        if server:
            title = "[{} {}".format(server, title)
        else:
            title = "[" + title

        filename = "".join((snapshot.name, cluster, title))
        filename = re.sub(r"[\[\]/\\:\*\?\"<>\|& ]", "", filename)
        filename += "{suffix}.png"

        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return title, media_url, media_path

    def get_series(self, metric, data):
        data = {k: v[0] for k, v in data.iteritems()}
        series = pd.Series(data)
        series.dropna()  # otherwise it may break kde
        if metric in constants.NON_ZERO_VALUES and (series == 0).all():
            return None
        series.index = series.index.astype("uint64")
        series.rename(lambda x: x - series.index.values.min(), inplace=True)
        series.rename(lambda x: x / 1000, inplace=True)  # ms -> s
        return series

    def extract(self, meta):
        merge = defaultdict(list)
        merge_cluster = ""
        for observable, snapshot in meta:
            data = self.query_data(snapshot,
                                   observable.cluster, observable.server,
                                   observable.bucket,
                                   observable.name, observable.collector)
            if data:
                series = self.get_series(metric=observable.name, data=data)
                if series is not None:
                    merge["series"].append(series)
                    if snapshot.name == "all_data":
                        merge["labels"].append(observable.cluster)
                    else:
                        merge["labels"].append(snapshot.name)
            merge_cluster += observable.cluster
        title, url, filename = self.generate_png_meta(snapshot,
                                                      merge_cluster,
                                                      observable.server,
                                                      observable.bucket,
                                                      observable.name)

        return merge["series"], merge["labels"], title, filename, url

    def detect_rebalance(self, observables):
        rebalances = []
        if observables[0][0].name == "rebalance_progress":
            series, _, _, _, _ = self.extract(observables)
            for s in series:
                s = s.dropna()
                if (s == 0).all():
                    return []
                rebalance = s[s > 0]
                rebalances.append((rebalance.index[0], rebalance.index[-1]))
        return rebalances

    def plot(self, metrics):
        apply_results = list()
        metrics = tuple(metrics)
        rebalances = self.detect_rebalance(metrics[0])

        for data in self.eventlet_pool.imap(self.extract, metrics):
            series, labels, title, filename, url = data
            if series:
                metric = title.split()[-1]
                ylabel = constants.LABELS.get(metric, metric)

                chart_ids = [""]
                if metric in constants.HISTOGRAMS:
                    chart_ids += ["_histo"]
                if metric in constants.ZOOM_HISTOGRAMS:
                    chart_ids += ["_lt90", "_gt90"]
                if metric in constants.KDE:
                    chart_ids += ["_kde"]
                if metric in constants.SMOOTH_SUBPLOTS:
                    chart_ids[0] = "_subplot"
                    chart_ids += ["_score"]

                for chart_id in chart_ids:
                    fname = filename.format(suffix=chart_id)
                    if not os.path.exists(fname):
                        apply_results.append(self.mp_pool.apply_async(
                            plot_as_png,
                            args=(fname, series, labels, ylabel, chart_id,
                                  rebalances)
                        ))
                    self.urls.append([title, url.format(suffix=chart_id)])
                    self.images.append(fname)
        for result in apply_results:
            result.get()
