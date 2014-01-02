import pandas as pd

from cbmonitor.helpers import SerieslyHandler
from cbmonitor.plotter import Plotter
from cbmonitor.plotter.reports import Report


class Analyzer(object):

    def __init__(self):
        self.seriesly = SerieslyHandler()

    def get_time_series(self, observables):
        for ol in observables:
            for observable in ol:
                if observable:
                    raw_data = self.seriesly.query_data(observable)
                    if raw_data:
                        s = pd.Series(raw_data)
                        if len(s.unique()) == 1:
                            continue
                        s = pd.rolling_median(s, window=3)
                        title = Plotter.generate_title(observable)
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
