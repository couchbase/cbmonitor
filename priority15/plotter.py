#!/usr/bin/env python
from optparse import OptionParser
import subprocess
import sys
from tempfile import mkdtemp

from matplotlib.pyplot import figure, grid
from seriesly import Seriesly


def get_metric(db, metric):
    """Query data using metric as key"""
    # get query response
    query_params = {'group': 15000,  # 15 seconds
                    'ptr': '/{0}'.format(metric),
                    'reducer': 'avg'}
    response = db.query(query_params)

    # convert data and generate sorted lists of timestamps and values
    data = dict((k, v[0]) for k, v in response.iteritems())

    timestamps = list()
    values = list()

    for timestamp, value in sorted(data.iteritems()):
        timestamps.append(int(timestamp))
        values.append(value)

    # Substract first timestamp; conver to seconds
    timestamps = [(key - timestamps[0]) / 1000 for key in timestamps]

    return timestamps, values


def plot_metric(metric, keys, values, outdir):
    """Plot chart and save it as PNG file"""
    fig = figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.set_title(metric)
    ax.set_xlabel('Time elapsed (sec)')

    grid()

    ax.plot(keys, values, '.')
    fig.savefig('{0}/{1}.png'.format(outdir, metric))


def parse_args():
    """Parse CLI arguments"""
    usage = "usage: %prog database\n\n" +\
            "Example: %prog ns_db "

    parser = OptionParser(usage)
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        sys.exit()

    return args[0]


def main():
    # parse database name from cli arguments
    db_name = parse_args()

    # initialize seriesly client
    db = Seriesly()[db_name]

    # get a set of all unique keys
    all_docs = db.get_all()
    all_keys = \
        set(key for doc in all_docs.itervalues() for key in doc.iterkeys())

    # plot all metrics to PNG images
    outdir = mkdtemp()
    for metric in all_keys:
        print metric
        if '/' not in metric:  # views and xdcr stuff
            keys, values = get_metric(db, metric)
            plot_metric(metric, keys, values, outdir)

    try:
        subprocess.call(['convert', '{0}/*'.format(outdir), 'report.pdf'])
        print "PDF report was successfully generated!"
    except OSError:
        print "All images saved to: {0}".format(outdir)


if __name__ == '__main__':
    main()
