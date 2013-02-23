from eventlet import GreenPool

from cbagent.collectors import Collector


class ActiveTasks(Collector):

    def __init__(self, settings):
        super(ActiveTasks, self).__init__(settings)
        self.pool = GreenPool()
        self.pointers = list()
        self.update_metadata_enabled = settings.update_metadata

    def update_metadata(self):
        """Update cluster's, server's and bucket's metadata"""
        self.mc.add_cluster()

        for bucket in self._get_buckets():
            self.mc.add_bucket(bucket)

        for node in self._get_nodes():
            self.mc.add_server(node)

    def _update_metric_metadata(method):
        def wrapper(self, metric, value, bucket=None, server=None):
            pointer = hash((metric, bucket, server))
            if pointer not in self.pointers and self.update_metadata_enabled:
                self.pointers.append(pointer)
                self.mc.add_metric(metric, bucket, server)
            return method(self, metric, value, bucket, server)
        return wrapper

    @_update_metric_metadata
    def _extend_samples(self, metric, value, bucket=None, server=None):
        sample = {metric: value}
        if server is not None:
            if self._samples.get(bucket) is None:
                self._samples[bucket] = {}
            if self._samples[bucket].get(server) is None:
                self._samples[bucket][server] = {}
            self._samples[bucket][server].update(sample)
        elif bucket is not None:
            if self._samples.get(bucket) is None:
                self._samples[bucket] = {}
            self._samples[bucket].update(sample)
        else:
            self._samples.update(sample)

    @staticmethod
    def _gen_couch_task_id(task, metric):
        return "{0}_{1}_{2}".format(task["type"], task.get("indexer_type", ""),
                                    metric)

    def _get_couchdb_tasks(self, server):
        tasks = self._get("/_active_tasks", server=server, port=8092)
        for task in tasks:
            if "index_barrier" in task["type"]:
                self._extend_samples("running_" + task["type"], task["running"])
                self._extend_samples("waiting_" + task["type"], task["waiting"])
            elif task["type"] in ("view_compaction", "indexer"):
                bucket = task.get("set", "")
                for metric in ("changes_done", "total_changes", "progress"):
                    value = task.get(metric, None)
                    if value is not None:
                        metric = self._gen_couch_task_id(task, metric)
                        self._extend_samples(metric, value, bucket, server)

    @staticmethod
    def _gen_ns_server_task_id(task, metric):
        return "{0}{1}_{2}".format(task["type"], task.get("designDocument", ""),
                                   metric)

    def _get_ns_server_tasks(self):
        tasks = self._get("/pools/default/tasks")
        for task in tasks:
            bucket = task.get("bucket", None)
            for metric in ("changesDone", "totalChanges", "progress"):
                value = task.get(metric, None)
                if value is not None:
                    metric = self._gen_ns_server_task_id(task, metric)
                    self._extend_samples(metric, value, bucket)

    def collect(self):
        """Collect info about ns_server and couchdb active tasks"""
        self._samples = {}
        self._get_ns_server_tasks()
        for _ in self.pool.imap(self._get_couchdb_tasks, self._get_nodes()):
            continue

        self._samples = {"metric": {self.cluster: self._samples}}
        self.store.append(self._samples)
