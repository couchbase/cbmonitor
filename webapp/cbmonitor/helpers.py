from calendar import timegm

import seriesly


class SerieslyHandler(object):

    """Simple handler for data stored in seriesly database."""

    def __init__(self):
        self.db = seriesly.Seriesly()
        self.all_dbs = self.db.list_dbs()

    @staticmethod
    def build_dbname(cluster, server, bucket, collector):
        """Each seriesly db name is built from observable object attributes."""
        db_name = (collector or "") + cluster + (bucket or "") + (server or "")
        for char in "[]/\;.,><&*:%=+@!#^()|?^'\"":
            db_name = db_name.replace(char, "")
        return db_name

    def query_data(self, observable):
        """Read data from seriesly database. Use snapshot time range if
        possible."""
        query_params = {"ptr": "/{}".format(observable.name), "reducer": "avg",
                        "group": 5000}
        if observable.snapshot.ts_from and observable.snapshot.ts_to:
            ts_from = timegm(observable.snapshot.ts_from.timetuple()) * 1000
            ts_to = timegm(observable.snapshot.ts_to.timetuple()) * 1000
            group = max((ts_from - ts_to) / 500, 5000)  # min 5s; max 500 points
            query_params.update({"group": group, "from": ts_from, "to": ts_to})
        db_name = self.build_dbname(observable.snapshot.cluster.name,
                                    observable.server, observable.bucket,
                                    observable.collector)
        if db_name in self.all_dbs:
            try:
                raw_data = self.db[db_name].query(query_params)
                return {k: v[0] for k, v in raw_data.items()}
            except seriesly.exceptions.ConnectionError:
                return
        else:
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
