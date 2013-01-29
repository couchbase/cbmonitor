from seriesly import Seriesly

from store import Store


class SerieslyStore(Store):

    def __init__(self, host, dbname):
        self.seriesly = Seriesly(host)
        if dbname not in self.seriesly.list_dbs():
            self.seriesly.create_db(dbname)
        self.dbname = dbname

    def append(self, data):
        self.seriesly[self.dbname].append(data)
