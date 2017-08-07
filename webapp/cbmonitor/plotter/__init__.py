import dateutil.parser
import os
import re
from collections import defaultdict
from itertools import cycle
from multiprocessing import Pool, cpu_count

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from django.conf import settings
from eventlet import GreenPool

from cbmonitor.helpers import SerieslyHandler
from cbmonitor.plotter import constants
from cbmonitor.plotter.reports import Report

matplotlib.rcParams.update({
    'axes.formatter.limits': (-6, 6),
    'axes.grid': True,
    'axes.linewidth': 0.4,
    'axes.xmargin': 0,
    'font.size': 5,
    'grid.linestyle': 'dotted',
    'grid.linewidth': 0.5,
    'legend.fancybox': True,
    'legend.loc': 'upper right',
    'legend.markerscale': 2,
    'legend.numpoints': 1,
    'lines.antialiased': False,
    'lines.linestyle': 'None',
    'lines.marker': '.',
    'lines.markersize': 1.8,
    'xtick.direction': 'in',
    'xtick.major.size': 4,
    'xtick.major.width': 0.4,
    'ytick.direction': 'in',
    'ytick.major.size': 4,
    'ytick.major.width': 0.4,
    'ytick.right': True,
})


def plot_as_png(filename, series, labels, colors, ylabel, chart_id, rebalances):
    """Primary routine that serves as plot selector. The function and all
    sub-functions are defined externally in order to be pickled."""
    fig = plt.figure(figsize=(4.66, 2.625))
    ax = init_ax(fig)

    if chart_id in ("_lt90", "_gt80", "_histo"):
        plot_percentiles(ax, series, labels, colors, ylabel, chart_id)
    else:
        plot_time_series(ax, series, labels, colors, ylabel)
        highlight_rebalance(rebalances, colors)

    legend = ax.legend()
    legend.get_frame().set_linewidth(0.5)

    fig.tight_layout()
    fig.savefig(filename, dpi=200)
    plt.close()


def init_ax(fig, dim=(1, 1, 1)):
    """Initialize subplot object with given dimensions within figure object."""
    ax = fig.add_subplot(*dim)
    ax.ticklabel_format(useOffset=False)
    return ax


def plot_time_series(ax, series, labels, colors, ylabel=None):
    """Simple time series plot or sub-plot."""
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.set_xlabel("Time elapsed, sec")
    for s, label, color in zip(series, labels, colors):
        ax.plot(s.index, s, label=label, color=color)
    ymin, ymax = ax.get_ylim()
    plt.ylim(ymin=0, ymax=max(1, ymax * 1.05))


def plot_percentiles(ax, series, labels, colors, ylabel, chart_id):
    """Bar plot with 3 possible percentile ranges and sub-ranges:
    -- 1 to 99 (linear)
    -- 1 to 89 (linear)
    -- 80 to 99.999 (non-linear, pre-defined)
    """
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Percentile")
    width = cycle((0.6, 0.4))
    align = cycle(("edge", "center"))
    if chart_id == "_lt90":
        percentiles = range(1, 90)
        x = percentiles
        plt.xlim(0, 90)
    elif chart_id == "_gt80":
        percentiles = (80, 85, 90, 95, 97.5, 99, 99.9, 99.99, 99.999)
        x = range(len(percentiles))
        plt.xticks(x, percentiles)
    else:
        percentiles = range(1, 100)
        x = percentiles
        plt.xlim(0, 100)
    for s, label, color in zip(series, labels, colors):
        y = np.percentile(s, percentiles)
        ax.bar(x, y, linewidth=0.0, label=label,
               width=width.next(), align=align.next(), color=color)


def highlight_rebalance(rebalances, colors):
    """Transparent span that highlights rebalance start and end. Makes sense
    only for similar reports (e.g., rebalance+views vs. rebalance+views).
    Otherwise disorder in colors may happen."""
    for (start, end), color in zip(rebalances, colors):
        plt.axvspan(start, end, facecolor=color, alpha=0.1, linewidth=0.5)


class Colors(object):

    def __init__(self):
        self.cycle = cycle(constants.PALETTE)

    def next(self):
        return self.cycle.next()


class Plotter(object):

    """Plotter helper that reads data from seriesly database and generates
    handy charts with url/filesystem meta information."""

    def __init__(self):
        self.urls = list()  # The only thing that caller (view) needs

        self.eventlet_pool = GreenPool()  # for seriesly requests
        self.mp_pool = Pool(cpu_count())  # for plotting

        self.seriesly = SerieslyHandler()

    def __del__(self):
        self.mp_pool.close()

    @staticmethod
    def generate_title(observable):
        """[server/bucket] metric"""
        metric = observable.name.replace("/", "_")
        if observable.bucket:
            return "[{}] {}".format(observable.bucket, metric)
        elif observable.server:
            return "[{}] {}".format(observable.server, metric)
        elif observable.index and "." in observable.index:
            name = observable.index.split(".")
            return "[{}] [{}] {}".format(name[0], name[1], metric)
        else:
            return metric

    def generate_png_meta(self, snapshot, cluster, title):
        """Generate output filenames and URLs based on object attributes."""
        filename = "".join((snapshot, cluster, title))
        filename = re.sub(r"[\[\]/\\:\*\?\"<>\|& ]", "", filename)
        filename += "{suffix}.png"

        media_url = settings.MEDIA_URL + filename
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        return media_url, media_path

    def get_series(self, metric, data):
        """Convert raw data to Pandas time series."""
        series = pd.Series(data)
        series.dropna()  # otherwise it may break kde
        if metric in constants.NON_ZERO_VALUES and (series == 0).all():
            return None
        series.rename(lambda x: dateutil.parser.parse(x), inplace=True)
        series.rename(lambda x: int(x.strftime('%s')), inplace=True)
        series.rename(lambda x: x - series.index.values.min(), inplace=True)
        return series

    def extract(self, observables, skip_df=False):
        """Top-level abstraction for data and metadata extraction."""
        merge = defaultdict(list)
        title = ""
        colors = Colors()
        for observable in observables:
            color = colors.next()
            if observable:
                data = self.seriesly.query_data(observable)
                if data:
                    series = self.get_series(metric=observable.name, data=data)
                    if series is not None:
                        merge["series"].append(series)
                        merge["labels"].append(observable.snapshot.name)
                        merge["colors"].append(color)
                        merge["clusters"].append(observable.snapshot.cluster.name)
                        merge["snapshots"].append(observable.snapshot.name)
                        title = self.generate_title(observable)

        url, fname = self.generate_png_meta("".join(merge["snapshots"]),
                                            "".join(merge["clusters"]),
                                            title)

        return merge["series"], merge["labels"], merge["colors"], title, fname, url

    def detect_rebalance(self, observables):
        """Check first observable object which is expected to be rebalance
        progress characteristic."""
        rebalances = []
        if observables[0] and observables[0].name == "rebalance_progress":
            series, _, _, _, _, _ = self.extract(observables, skip_df=True)
            for s in series:
                s = s.dropna()
                if (s == 0).all():
                    return []
                rebalance = s[s > 0]
                rebalances.append((rebalance.index[0], rebalance.index[-1]))
        return rebalances

    def plot(self, snapshots):
        """End-point method that orchestrates concurrent extraction and
        plotting."""
        observables = Report(snapshots)()

        rebalances = self.detect_rebalance(observables[0])

        # Asynchronously extract data
        apply_results = list()
        for data in self.eventlet_pool.imap(self.extract, observables):
            series, labels, colors, title, filename, url = data
            if series:
                metric = title.split()[-1]
                ylabel = constants.LABELS.get(metric, metric)

                chart_ids = [""]
                if metric in constants.HISTOGRAMS:
                    chart_ids += ["_histo"]
                if metric in constants.ZOOM_HISTOGRAMS:
                    chart_ids += ["_lt90", "_gt80"]

                for chart_id in chart_ids:
                    fname = filename.format(suffix=chart_id)
                    if not os.path.exists(fname):
                        apply_results.append(self.mp_pool.apply_async(
                            plot_as_png,
                            args=(fname,
                                  series, labels, colors, ylabel, chart_id,
                                  rebalances)
                        ))
                    self.urls.append([title, url.format(suffix=chart_id)])
        # Plot all charts in parallel
        for result in apply_results:
            result.get()
