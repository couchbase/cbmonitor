from django.core.exceptions import ObjectDoesNotExist

from cbmonitor import models


class Report(object):

    def __new__(cls, snapshots, report_type):
        try:
            return eval(report_type)(snapshots)
        except (NameError, SyntaxError):
            raise NotImplementedError("Unknown report type")


class BaseReport(object):

    metrics = {
        "ns_server": [
            "ops",
            "cmd_get",
            "cmd_set",
            "delete_hits",
            "curr_connections",
            "curr_items",
            "mem_used",
            "vb_active_resident_items_ratio",
            "vb_replica_resident_items_ratio",
            "ep_num_value_ejects",
            "disk_write_queue",
            "ep_cache_miss_rate",
            "ep_bg_fetched",
            "ep_diskqueue_drain",
            "avg_bg_wait_time",
            "avg_disk_commit_time",
            "avg_disk_update_time",
            "couch_docs_data_size",
            "couch_docs_actual_disk_size",
            "couch_docs_fragmentation",
            "couch_total_disk_size",
        ],
        "atop": [
            "beam.smp_rss",
            "beam.smp_vsize",
            "beam.smp_cpu",
            "memcached_cpu"
        ]
    }

    def __init__(self, snapshots):
        self.snapshots = snapshots
        clusters = [cluster for snapshot, cluster in snapshots]
        self.buckets = models.Bucket.objects.filter(cluster=clusters[0])
        self.servers = models.Server.objects.filter(cluster=clusters[0])

    def merge_metrics(self):
        base_metrics = BaseReport.metrics
        for collector in set(base_metrics) & set(self.metrics):
            self.metrics[collector] += base_metrics[collector]
        self.metrics = dict(base_metrics, **self.metrics)

    def __iter__(self):
        for collector, metrics in self.metrics.iteritems():
            for metric in metrics:
                for bucket in self.buckets:
                    observables = []
                    for snapshot, cluster in self.snapshots:
                        try:
                            _bucket = models.Bucket.objects.get(
                                cluster=cluster,
                                name=bucket.name
                            )
                            observable = models.Observable.objects.get(
                                cluster=cluster,
                                type_id="metric",
                                collector=collector,
                                name=metric,
                                server__isnull=True,
                                bucket=_bucket,
                            )
                            observables.append((observable, snapshot))
                        except ObjectDoesNotExist:
                            pass
                    if observables:
                        yield observables
            if collector == "atop":
                for metric in metrics:
                    for server in self.servers:
                        observables = []
                        for snapshot, cluster in self.snapshots:
                            try:
                                _server = models.Server.objects.get(
                                    cluster=cluster,
                                    address=server.address
                                )
                                observable = models.Observable.objects.get(
                                    cluster=cluster,
                                    type_id="metric",
                                    collector=collector,
                                    name=metric,
                                    server=_server,
                                    bucket__isnull=True,
                                )
                                observables.append((observable, snapshot))
                            except ObjectDoesNotExist:
                                pass
                        if observables:
                            yield observables


class BaseXdcrReport(BaseReport):

    def __init__(self, *args, **kwargs):
        self.metrics = {
            "xdcr_lag": [
                "xdcr_lag",
                "xdcr_persistence_time",
                "xdcr_diff",
            ],
            "ns_server": [
                "replication_changes_left",
                "xdc_ops",
                "ep_num_ops_get_meta",
                "ep_num_ops_set_meta",
                "ep_num_ops_del_meta",
            ]
        }
        self.merge_metrics()
        super(BaseXdcrReport, self).__init__(*args, **kwargs)


class BaseKVReport(BaseReport):

    def __init__(self, *args, **kwargs):
        self.metrics = {
            "spring_latency": [
                "latency_set",
                "latency_get",
            ],
        }
        self.merge_metrics()
        super(BaseKVReport, self).__init__(*args, **kwargs)


class BaseViewsReport(BaseReport):

    def __init__(self, *args, **kwargs):
        self.metrics = {
            "spring_query_latency": [
                "latency_query",
            ],
            "ns_server": [
                "couch_views_ops",
                "couch_views_data_size",
                "couch_views_actual_disk_size",
                "couch_views_fragmentation",
            ]
        }
        self.merge_metrics()
        super(BaseViewsReport, self).__init__(*args, **kwargs)

class BaseTuqReport(BaseReport):

    def __init__(self, *args, **kwargs):
        self.metrics = {
            "spring_tuq_latency": [
                "latency_query",
                "latency_tuq",
            ],
            "ns_server": [
                "couch_views_ops",
                "couch_views_data_size",
                "couch_views_actual_disk_size",
                "couch_views_fragmentation",
            ]
        }
        self.merge_metrics()
        super(BaseTuqReport, self).__init__(*args, **kwargs)

class BaseRebalanceReport(BaseReport):

    def __iter__(self):
        observables = []
        for snapshot, cluster in self.snapshots:
            try:
                observable = models.Observable.objects.get(
                    cluster=cluster,
                    type_id="metric",
                    collector="active_tasks",
                    name="rebalance_progress",
                    server__isnull=True,
                    bucket__isnull=True,
                )
                observables.append((observable, snapshot))
            except ObjectDoesNotExist:
                pass
        if observables:
            yield observables
        for observables in super(BaseRebalanceReport, self).__iter__():
            yield observables


class BaseRebalanceViewsReport(BaseRebalanceReport, BaseViewsReport):

    def __init__(self, *args, **kwargs):
        super(BaseRebalanceReport, self).__init__(*args, **kwargs)


class BaseRebalanceXdcrReport(BaseRebalanceReport, BaseXdcrReport):

    def __init__(self, *args, **kwargs):
        super(BaseRebalanceReport, self).__init__(*args, **kwargs)


class FullReport(BaseReport):

    def __init__(self, snapshots):
        super(FullReport, self).__init__(snapshots)

        clusters = [c for s, c in self.snapshots]
        metrics = models.Observable.objects.filter(cluster=clusters[0],
                                                   server__isnull=True)
        self.metrics = set(metric.name for metric in metrics)

    def __iter__(self):
        for collector in ("ns_server", ):
            for metric in self.metrics:
                for bucket in self.buckets:
                    observables = []
                    for snapshot, cluster in self.snapshots:
                        try:
                            _bucket = models.Bucket.objects.get(
                                cluster=cluster,
                                name=bucket.name
                            )
                            observable = models.Observable.objects.get(
                                cluster=cluster,
                                type_id="metric",
                                collector=collector,
                                name=metric,
                                server__isnull=True,
                                bucket=_bucket,
                            )
                            observables.append((observable, snapshot))
                        except ObjectDoesNotExist:
                            pass
                    if observables:
                        yield observables
