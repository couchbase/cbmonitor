import pandas as pd

from cbmonitor.helpers import SerieslyHandler
from cbmonitor.plotter.constants import NON_ZERO_VALUES
from cbmonitor.plotter.reports import Report


class Analyzer(object):

    def __init__(self):
        self.seriesly = SerieslyHandler()

    def generate_title(self, observable):
        metric = observable.name.replace("/", "_")
        title = "{}] {}".format(observable.bucket, metric)
        if observable.server:
            title = "[{} {}".format(observable.server, title)
        else:
            title = "[" + title
        return title

    def get_time_series(self, observables):
        for ol in observables:
            for observable in ol:
                if observable:
                    raw_data = self.seriesly.query_data(observable)
                    if raw_data:
                        s = pd.Series(raw_data)
                        if observable.name in NON_ZERO_VALUES and (s == 0).all():
                            continue
                        s = pd.rolling_median(s, window=5)
                        title = self.generate_title(observable)
                        yield title, s

    def create_data_frame(self, observables):
        df = pd.DataFrame()
        for title, series in self.get_time_series(observables):
            new_df = pd.DataFrame(data=series, columns=(title, ))
            df = pd.concat((df, new_df), axis=1)
        return df

    def corr(self, snapshots):
        observables = Report(snapshots)()
        df = self.create_data_frame(observables)
        return df.columns.values.tolist(), df.corr().fillna(0).values.tolist()
