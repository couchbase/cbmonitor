from cbagent.collectors import Collector


class ActiveTasks(Collector):

    def __init__(self, settings):
        super(ActiveTasks, self).__init__(settings)
        self.pointers = list()
        self.update_metadata_enabled = settings.update_metadata

    def update_metadata(self):
        """Update cluster's, server's and bucket's metadata"""
        self.mc.add_cluster()

        for bucket in self._get_buckets():
            self.mc.add_bucket(bucket)

        for node in self._get_nodes():
            self.mc.add_server(node)

    @staticmethod
    def _build_couchdb_task_id(task, metric):
        return "{0}_{1}_{2}".format(task["type"], task.get("indexer_type", ""),
                                    metric)

    def _get_couchdb_tasks(self, server):
        tasks = self._get("/_active_tasks", server=server, port=8092)
        for task in tasks:
            if "index_barrier" in task["type"]:
                yield "running_" + task["type"], task["running"], None, None
                yield "waiting_" + task["type"], task["waiting"], None, None
            elif task["type"] in ("view_compaction", "indexer"):
                for metric in ("changes_done", "total_changes", "progress"):
                    value = task.get(metric, None)
                    if value is not None:
                        metric = self._build_couchdb_task_id(task, metric)
                        bucket = task.get("set", "")
                        yield metric, value, bucket, server

    @staticmethod
    def _build_ns_server_task_id(task, metric):
        return "{0}{1}_{2}".format(task["type"], task.get("designDocument", ""),
                                   metric)

    def _get_ns_server_tasks(self):
        tasks = self._get("/pools/default/tasks")
        for task in tasks:
            bucket = task.get("bucket", None)
            for metric in ("changesDone", "totalChanges", "progress"):
                value = task.get(metric, 0)
                metric = self._build_ns_server_task_id(task, metric)
                yield metric, value, bucket

    def _append(self, metric, value, bucket=None, server=None):
        pointer = hash((metric, bucket, server))
        if pointer not in self.pointers and self.update_metadata_enabled:
            self.pointers.append(pointer)
            self.mc.add_metric(metric, bucket, server, collector="active_tasks")

        data = {metric: value}
        self.store.append(data, cluster=self.cluster, bucket=bucket,
                          server=server, collector="active_tasks")

    def collect(self):
        """Collect info about ns_server and couchdb active tasks"""
        for metric, value, bucket in self._get_ns_server_tasks():
            self._append(metric, value, bucket=bucket)
        for node in self._get_nodes():
            for metric, value, bucket, server in self._get_couchdb_tasks(node):
                self._append(metric, value, bucket, server)
