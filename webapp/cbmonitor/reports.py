from collections import OrderedDict, defaultdict, namedtuple

from django.core.exceptions import ObjectDoesNotExist

from cbmonitor import models


class Report(object):

    def __new__(cls, snapshots, report_type):
        try:
            return eval(report_type)(snapshots)
        except (NameError, SyntaxError):
            raise NotImplementedError("Unknown report type")


Observable = namedtuple(
    'Observable', ['cluster', 'server', 'bucket', 'name', 'collector']
)


class BaseReport(object):

    metrics = OrderedDict((
        ("xdcr_lag", [
            "xdcr_lag",
            "xdcr_persistence_time",
            "xdcr_diff",
        ]),
        ("spring_query_latency", [
            "latency_query",
        ]),
        ("spring_tuq_latency", [
            "latency_query",
            "latency_tuq",
        ]),
        ("spring_latency", [
            "latency_set",
            "latency_get",
        ]),
        ("sync_gateway", [
            "Sys",
            "Alloc",
            "HeapAlloc",
            "HeapObjects",
            "PauseNs",
            "PauseTotalNs",
            "PausesPct",
            "NumGC",
        ]),
        ("active_tasks", [
            "bucket_compaction_progress",
        ]),
        ("ns_server", [
            "couch_views_ops",
            "ops",
            "cmd_get",
            "cmd_set",
            "delete_hits",
            "cas_hits",
            "xdc_ops",
            "ep_num_ops_get_meta",
            "ep_num_ops_set_meta",
            "ep_num_ops_del_meta",
            "replication_changes_left",
            "replication_size_rep_queue",
            "replication_rate_replication",
            "replication_bandwidth_usage",
            "replication_work_time",
            "replication_commit_time",
            "replication_active_vbreps",
            "replication_waiting_vbreps",
            "replication_num_checkpoints",
            "replication_num_failedckpts",
            "replication_meta_latency_wt",
            "replication_docs_latency_wt",
            "curr_connections",
            "hibernated_waked",
            "curr_items",
            "mem_used",
            "ep_meta_data_memory",
            "vb_active_resident_items_ratio",
            "vb_replica_resident_items_ratio",
            "ep_num_value_ejects",
            "ep_tmp_oom_errors",
            "disk_write_queue",
            "ep_cache_miss_rate",
            "ep_bg_fetched",
            "ep_diskqueue_drain",
            "avg_bg_wait_time",
            "avg_disk_commit_time",
            "avg_disk_update_time",
            "couch_docs_data_size",
            "couch_docs_actual_disk_size",
            "couch_views_data_size",
            "couch_views_actual_disk_size",
            "couch_total_disk_size",
            "couch_docs_fragmentation",
            "couch_views_fragmentation",
        ]),
        ("atop", [
            "sync_gateway_rss",
            "sync_gateway_cpu",
            "beam.smp_rss",
            "beam.smp_cpu",
            "memcached_cpu",
        ]),
        ("iostat", [
            "data_rbps",
            "data_wbps",
            "data_avgqusz",
            "data_util",
            "index_rbps",
            "index_wbps",
            "index_avgqusz",
            "index_util",
        ]),
    ))

    def __init__(self, snapshots):
        self.snapshots = snapshots
        clusters = [cluster for snapshot, cluster in snapshots]
        self.buckets = models.Bucket.objects.filter(cluster=clusters[0])
        self.servers = models.Server.objects.filter(cluster=clusters[0])

    def get_all_observables(self):
        all_observables = defaultdict(dict)
        for snapshot, cluster in self.snapshots:
            cluster_name = cluster.name
            for bucket in self.buckets:
                bucket_name = bucket.name
                _bucket = models.Bucket.objects.get(cluster=cluster,
                                                    name=bucket.name)
                observables = defaultdict(dict)
                for o in models.Observable.objects.filter(cluster=cluster,
                                                          bucket=_bucket,
                                                          server__isnull=True):
                    observables[o.collector][o.name] = Observable(
                        cluster_name, "", bucket_name, o.name, o.collector
                    )
                all_observables[bucket.name][cluster.name] = observables
            for server in self.servers:
                server_address = server.address
                _server = models.Server.objects.get(cluster=cluster,
                                                    address=server.address)
                observables = defaultdict(dict)
                for o in models.Observable.objects.filter(cluster=cluster,
                                                          bucket__isnull=True,
                                                          server=_server):
                    observables[o.collector][o.name] = Observable(
                        cluster_name, server_address, "", o.name, o.collector
                    )
                all_observables[server.address][cluster.name] = observables
        return all_observables

    def __iter__(self):
        _all = self.get_all_observables()

        for collector, metrics in self.metrics.iteritems():
            if collector in ("atop", "iostat", "sync_gateway"):
                for metric in metrics:
                    for server in self.servers:
                        observables = []
                        for snapshot, cluster in self.snapshots:
                            observable = _all[server.address][cluster.name][collector].get(metric)
                            if observable:
                                observables.append((observable, snapshot))
                        if observables:
                            yield observables
            else:
                for metric in metrics:
                    for bucket in self.buckets:
                        observables = []
                        for snapshot, cluster in self.snapshots:
                            observable = _all[bucket.name][cluster.name][collector].get(metric)
                            if observable:
                                observables.append((observable, snapshot))
                        if observables:
                            yield observables


class BaseRebalanceReport(BaseReport):

    def __iter__(self):
        observables = []
        for snapshot, cluster in self.snapshots:
            try:
                observable = models.Observable.objects.get(
                    cluster=cluster,
                    collector="active_tasks",
                    name="rebalance_progress",
                    server__isnull=True,
                    bucket__isnull=True,
                )
                observable = Observable(
                    cluster.name, "", "", observable.name, observable.collector
                )
                observables.append((observable, snapshot))
            except ObjectDoesNotExist:
                pass
        if observables:
            yield observables
        for observables in super(BaseRebalanceReport, self).__iter__():
            yield observables


class BaseXdcrReport(BaseReport):

    pass


class BaseKVReport(BaseReport):

    pass


class BaseViewsReport(BaseReport):

    pass


class BaseTuqReport(BaseReport):

    pass


class BaseRebalanceViewsReport(BaseRebalanceReport):

    pass


class BaseRebalanceXdcrReport(BaseRebalanceReport):

    pass


class SyncGatewayReport(BaseReport):

    pass
