import os
from itertools import cycle

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import requests
from django.conf import settings

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


def plot_as_png(filename, series, labels, colors, ylabel, chart, rebalances):
    """Primary routine that serves as plot selector. The function and all
    sub-functions are defined externally in order to be pickled."""
    fig = plt.figure(figsize=(4.66, 2.625))
    ax = init_ax(fig)

    if chart in ("_lt90", "_gt80", "_histo"):
        plot_percentiles(ax, series, labels, colors, ylabel, chart)
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


def plot_percentiles(ax, series, labels, colors, ylabel, chart):
    """Bar plot with 3 possible percentile ranges and sub-ranges:
    -- 1 to 99 (linear)
    -- 1 to 89 (linear)
    -- 80 to 99.999 (non-linear, pre-defined)
    """
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Percentile")
    width = cycle((0.6, 0.4))
    align = cycle(("edge", "center"))
    if chart == "_lt90":
        percentiles = range(1, 90)
        x = percentiles
        plt.xlim(0, 90)
    elif chart == "_gt80":
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
    """Add a transparent vertical span that highlights rebalance start and end.
    """
    for (start, end), color in zip(rebalances, colors):
        plt.axvspan(start, end, facecolor=color, alpha=0.1, linewidth=0.5)


def generate_title(observable):
    """Generate user-friendly chart title.

    The title is generated using this format:

        [server/bucket] metric.
    """
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


def generate_paths(clusters, metric, suffix):
    """Generate file name and URL using the unique attributes."""
    filename = "{}{}{}.png".format(''.join(clusters), metric, suffix)

    media_url = settings.MEDIA_URL + filename
    media_path = os.path.join(settings.MEDIA_ROOT, filename)

    return media_url, media_path


def build_dbname(cluster, server, bucket, index, collector):
    """Each seriesly db name is built from observable object attributes."""
    db_name = (collector or "") + cluster + (bucket or "") + (index or "") + (server or "")
    for char in "[]/\;.,><&*:%=+@!#^()|?^'\"":
        db_name = db_name.replace(char, "")
    return db_name


def generate_series(data):
    """Convert array of data points to Pandas series.

    perfdb returns data in the following format:

        [[timestamp, measurement], [timestamp, measurement], ...]

    The new series will create index based on timestamp. Measurements are used
    as values.

    The function also normalizes and sort data.
    """
    series = pd.Series(index=[d[0] for d in data], data=[d[1] for d in data])

    # Subtract the smallest timestamp value so that series starts from 0.
    starting_point = series.index.values.min()
    series.rename(lambda timestamp: timestamp - starting_point, inplace=True)

    # Convert milliseconds to seconds
    series.rename(lambda timestamp: timestamp / 10 ** 3, inplace=True)

    # Return data sorted by timestamp
    return series.sort_index()


def is_all_zeroes(metric, series):
    """Check if series should be skipped because it contains only zero values.
    """
    return metric in constants.NON_ZERO_VALUES and (series == 0).all()


def generate_chart_types(metric):
    charts = ["scatter"]
    if metric in constants.HISTOGRAMS:
        charts += ["_histo"]
    if metric in constants.ZOOM_HISTOGRAMS:
        charts += ["_lt90", "_gt80"]
    return charts


class Palette:

    def __init__(self):
        self.cycle = cycle(constants.PALETTE)

    def next(self):
        return self.cycle.next()


class DataClient:

    def __init__(self, host='127.0.0.1', port=8080):
        self.session = requests.Session()
        self.base_url = 'http://{}:{}/{{db}}/{{metric}}'.format(host, port)

    def get(self, db, metric):
        url = self.base_url.format(db=db, metric=metric)

        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()


class Plotter:

    def __init__(self):
        self.data_client = DataClient()

    def detect_rebalance(self, observables):
        if observables[0].name != "rebalance_progress":
            return []

        _series = []
        for observable in observables:
            series = self.get_series(observable)
            if series is not None and not (series == 0).all():
                _series.append(series)
            else:
                return []

        rebalances = []
        for series in _series:
            series = series[series > 0]  # Filter rebalance progress
            rebalances.append([series.index.min, series.index.max])
        return rebalances

    def get_series(self, observable):
        db = build_dbname(observable.cluster,
                          observable.server,
                          observable.bucket,
                          observable.index,
                          observable.collector)
        data = self.data_client.get(db, observable.name)
        if data:
            return generate_series(data)

    def generate_chart_data(self, observables):
        palette = Palette()

        _series = []
        _clusters = []
        _colors = []

        for observable in observables:
            color = palette.next()
            series = self.get_series(observable)
            if series is not None and not is_all_zeroes(observable.name, series):
                _series.append(series)
                _colors.append(color)
                _clusters.append(observable.cluster)

        return _series, _clusters, _colors

    def plot(self, snapshots):
        report = Report(snapshots).get_report()

        rebalances = self.detect_rebalance(report[0])

        images = []
        for observables in report:
            series, clusters, colors = self.generate_chart_data(observables)
            if not series:  # Bad or missing data
                continue

            metric = observables[0].name
            title = generate_title(observables[0])
            ylabel = constants.LABELS.get(metric, metric)

            for chart in generate_chart_types(metric):
                url, filename = generate_paths(clusters=clusters,
                                               metric=metric,
                                               suffix=chart)

                images.append([title, url])

                if not os.path.exists(filename):  # Try cache
                    plot_as_png(filename=filename,
                                series=series,
                                labels=clusters,
                                colors=colors,
                                ylabel=ylabel,
                                chart=chart,
                                rebalances=rebalances)
        return images
