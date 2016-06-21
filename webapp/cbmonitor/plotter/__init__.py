import os
import re
from collections import defaultdict
from itertools import cycle
from multiprocessing import Pool, cpu_count

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams.update({"font.size": 5})
matplotlib.rcParams.update({"lines.linewidth": 0.5})
matplotlib.rcParams.update({"lines.marker": "."})
matplotlib.rcParams.update({"lines.markersize": 3})
matplotlib.rcParams.update({"lines.linestyle": "None"})
matplotlib.rcParams.update({"axes.linewidth": 0.5})
matplotlib.rcParams.update({"axes.grid": True})
matplotlib.rcParams.update({"axes.formatter.limits": (-6, 6)})
matplotlib.rcParams.update({"legend.numpoints": 1})
matplotlib.rcParams.update({"legend.fancybox": True})
matplotlib.rcParams.update({"legend.markerscale": 1.5})
matplotlib.rcParams.update({"legend.loc": "best"})
matplotlib.rcParams.update({"legend.frameon": True})
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from django.conf import settings
from eventlet import GreenPool
from scipy import stats

from cbmonitor.helpers import SerieslyHandler
from cbmonitor.plotter import constants
from cbmonitor.plotter.reports import Report


def plot_as_png(filename, series, labels, colors, ylabel, chart_id, rebalances):
    """Primary routine that serves as plot selector. The function and all
    sub-functions are defined externally in order to be pickled."""
    fig = plt.figure(figsize=(4.66, 2.625))
    ax = init_ax(fig)

    if chart_id in ("_lt90", "_gt80", "_histo"):
        plot_percentiles(ax, series, labels, colors, ylabel, chart_id)
    elif chart_id == "_subplot":
        plot_subplot_frame(ax, ylabel)

        ax = init_ax(fig, dim=(2, 1, 1))
        plot_rolling_subplot(ax, series, labels, colors)
        highlight_rebalance(rebalances, colors)

        ax = init_ax(fig, dim=(2, 1, 2))
        plot_time_series(ax, series, labels, colors, ylabel=None)
        highlight_rebalance(rebalances, colors)
    elif chart_id == "_kde":
        plot_kde(ax, series, labels, colors, ylabel)
    elif chart_id == "_score":
        plot_score(ax, series, labels, colors, ylabel)
        highlight_rebalance(rebalances, colors)
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


def plot_score(ax, series, labels, colors, ylabel):
    """Score plot where score is calculated as 90th percentile. Quite useful
    for trends and dips analysis."""
    ax.set_ylabel("Percentile of score ({})".format(ylabel))
    ax.set_xlabel("Time elapsed, sec")
    for s, label, color in zip(series, labels, colors):
        scoref = lambda x: stats.percentileofscore(x, s.quantile(0.9))
        rolling_score = pd.rolling_apply(s, min(len(s) / 15, 40), scoref)
        ax.plot(s.index, rolling_score, label=label, color=color)
        plt.ylim(ymin=0, ymax=105)


def plot_kde(ax, series, labels, colors, ylabel):
    """KDE plot for values less than 99th percentile."""
    ax.set_ylabel("Kernel density estimation")
    ax.set_xlabel(ylabel)
    for s, label, color in zip(series, labels, colors):
        x = np.linspace(0, int(s.quantile(0.99)), 200)
        kde = stats.kde.gaussian_kde(s)
        ax.plot(x, kde(x), label=label, color=color)


def plot_subplot_frame(ax, ylabel):
    """Create a frame (common Y label) for figure with multiple subplots."""
    ax.set_ylabel(ylabel)
    map(lambda s: s.set_color("None"), ax.spines.values())
    ax.tick_params(top="off", bottom="off", left="off", right="off",
                   labelcolor="w")
    ax.grid(None)


def plot_rolling_subplot(ax, series, labels, colors):
    """Subplot with smoothed values (using moving median)."""
    for s, label, color in zip(series, labels, colors):
        rolling_median = pd.rolling_median(s, window=5)
        ax.plot(s.index, rolling_median, label=label, color=color)
        ymin, ymax = ax.get_ylim()
        plt.ylim(ymin=0, ymax=max(1, ymax * 1.05))


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
        series.index = series.index.astype("uint64")
        series.rename(lambda x: x - series.index.values.min(), inplace=True)
        series.rename(lambda x: x / 1000, inplace=True)  # ms -> s
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
                            args=(fname,
                                  series, labels, colors, ylabel, chart_id,
                                  rebalances)
                        ))
                    self.urls.append([title, url.format(suffix=chart_id)])
        # Plot all charts in parallel
        for result in apply_results:
            result.get()


class Comparator(Plotter):

    ALLOWED_NOISE = 0.1  # 10%
    MAX_CONFIDENCE = 7.0
    MIN_DATA_POINTS = 50
    MAX_SIZE_DIFF = 1.25  # 25%

    def estimate_diff(self, s1, s2):
        l1 = float(len(s1))
        l2 = float(len(s2))

        # Don't estimate time series that have huge difference in number of
        # elements
        if max(l1, l2) / min(l1, l2) > self.MAX_SIZE_DIFF:
            return -1

        # Don't estimate very small time series
        if min(l1, l2) < self.MIN_DATA_POINTS:
            return -1

        # Heuristic coefficient
        confidence = 0.0

        # Compare correlation coefficient
        if s1.corr(s2) < 0.9:
            confidence += 1.0
        # Compare mean values
        diff = abs(s1.mean() - s2.mean())
        if diff > self.ALLOWED_NOISE * s1.mean():
            confidence += 1.0
        # Compare 4 different percentiles
        for q in (0.5, 0.75, 0.9, 0.95):
            diff = abs(s1.quantile(q) - s2.quantile(q))
            if diff > self.ALLOWED_NOISE * s1.quantile(q):
                confidence += 0.5
        # Compare maximum values
        diff = abs(s1.max() - s2.max())
        if diff > self.ALLOWED_NOISE * s1.max():
            confidence += 1.0

        # Primary trend comparison
        t1 = pd.rolling_median(s1, window=5)
        t2 = pd.rolling_median(s1, window=5)
        if abs((t1 - t2).mean()) > self.ALLOWED_NOISE * t1.mean():
            confidence += 2.0

        # Return confidence as rounded percentage value
        return round(100 * confidence / self.MAX_CONFIDENCE)

    def compare(self, snapshots):
        """Return a list with metric/confidence pairs or None if snapshots are
        not comparable"""
        diffs = []
        invalid_counter = 0

        # Asynchronously extract data
        for data in self.eventlet_pool.imap(self.extract, Report(snapshots)()):
            series, _, _, title, _, _ = data
            if len(series) == 2:
                diff = self.estimate_diff(*series)
                if diff != - 1:
                    metric = title.split()[-1]
                    label = constants.LABELS.get(metric, metric)

                    diffs.append((
                        '{} ({})'.format(label, metric),
                        diff
                    ))

                    invalid_counter -= 1
                else:
                    invalid_counter += 1
        if invalid_counter < 0:
            return diffs
