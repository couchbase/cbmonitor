import seriesly


class SerieslyHandler(object):

    """Simple handler for data stored in seriesly database."""

    MIN_GROUP_INTERVAL = 1000  # 1 sec
    MAX_GROUP_INTERVAL = 5000  # 5 secs
    GROUPING_THRESHOLD = 14400  # start grouping when snapshot is longer than 4h

    def __init__(self):
        self.db = seriesly.Seriesly()
        self.all_dbs = self.db.list_dbs()

    @staticmethod
    def build_dbname(cluster, server, bucket, index, collector):
        """Each seriesly db name is built from observable object attributes."""
        db_name = (collector or "") + cluster + (bucket or "") + (index or "") + (server or "")
        for char in "[]/\;.,><&*:%=+@!#^()|?^'\"":
            db_name = db_name.replace(char, "")
        return db_name

    def query_data(self, observable):
        """Read data from seriesly database."""
        db_name = self.build_dbname(observable.snapshot.cluster.name,
                                    observable.server, observable.bucket,
                                    observable.index, observable.collector)
        if db_name in self.all_dbs:
            try:
                raw_data = self.db[db_name].get_all()
                return {k: v[observable.name] for k, v in raw_data.items()
                        if observable.name in v}
            except seriesly.exceptions.ConnectionError:
                return

    def query_raw_data(self, db_name, name):
        params = {"ptr": "/{}".format(name), "reducer": "avg", "group": 5000}
        if db_name in self.all_dbs:
            try:
                return self.db[db_name].query(params)
            except seriesly.exceptions.ConnectionError:
                return {}
        else:
            return {}
