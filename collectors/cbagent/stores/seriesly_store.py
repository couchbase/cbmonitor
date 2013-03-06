from seriesly import Seriesly

from store import Store


class SerieslyStore(Store):

    def __init__(self, host):
        self.seriesly = Seriesly(host)

    @staticmethod
    def build_dbname(cluster, server, bucket, collector):
        if collector:
            db_name = collector + cluster
        else:
            db_name = cluster
        if bucket:
            db_name += bucket
        if server:
            db_name += server.replace(".", "")
        return db_name

    def append(self, data, cluster=None, server=None, bucket=None,
               collector=None):
        db_name = self.build_dbname(cluster, server, bucket, collector)
        if db_name not in self.seriesly.list_dbs():
            self.seriesly.create_db(db_name)
        self.seriesly[db_name].append(data)
