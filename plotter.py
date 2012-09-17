from matplotlib.pyplot import figure, grid

from seriesly import Seriesly


def get_metric(metric):
    query_params = {
        'group': 15000,
        'ptr': '/{0}'.format(metric),
        'reducer': 'avg'
    }

    data = dict((k, float(v[0])) for k, v in s['ns_db'].query(query_params).iteritems())

    keys = list()
    values = list()

    for key, value in sorted(data.iteritems()):
        keys.append(int(key))
        values.append(value)

    keys = [(key - keys[0]) / 1000 for key in keys]


    return keys, values

def plot_metric(metric, keys, values):

    fig = figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.set_title(metric)
    ax.set_xlabel("Time elapsed (sec)")

    grid()

    ax.plot(keys, values)
    fig.savefig('/tmp/temp/{0}.png'.format(metric))


if __name__ == '__main__':
    s = Seriesly()

    all_docs = s['ns_db'].get_all()
    all_keys = set(key for doc in all_docs.itervalues()
                   for key in doc.iterkeys())

    for metric in all_keys:
        print metric
        if '/' not in metric:
            keys, values = get_metric(metric)
            plot_metric(metric, keys, values)
