from seriesly import Seriesly

from store import Store


class SerieslyStore(Store):

    def __init__(self, host):
        self.seriesly = Seriesly(host)

    def append(self, data, cluster):
        if cluster not in self.seriesly.list_dbs():
            self.seriesly.create_db(cluster)
        self.seriesly[cluster].append(data)
