from collections import OrderedDict, defaultdict, namedtuple

from cbmonitor import models


Observable = namedtuple(
    "Observable", ["snapshot", "server", "bucket", "name", "collector"]
)


class Report(object):

    """Provide all existing observables that meet following requirements:
    -- observable is in predefined dict of metrics (cls.METRICS)
    -- observable belongs to snapshot (input parameter)

    It supports arbitrary number of snapshots, each element includes a list of
    observables, one observable per snapshot. Yield is skipped in case of full
    snapshot mismatch (none of snapshot has corresponding observable object).
    """

    METRICS = OrderedDict((
        ("active_tasks", [
            "rebalance_progress",
            "bucket_compaction_progress",
        ]),
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
        ("observe", [
            "latency_observe",
        ]),
        ("durability", [
            "latency_persist_to",
            "latency_replicate_to",
        ]),
        ("fts_latency", [
            "cbft_latency_get",
            "elastic_latency_get",
            "elastic_cache_hit",
            "elastic_cache_size",
            "elastic_filter_cache_size",
            "elastic_active_search",
            "elastic_query_total"
        ]),
        ("spring_latency", [
            "latency_set",
            "latency_get",
        ]),
        ("sync_latency", [
            "gateway_push",
            "gateway_pull",
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
            "replication_rate_replication",
            "replication_bandwidth_usage",
            "replication_active_vbreps",
            "replication_waiting_vbreps",
            "replication_num_failedckpts",
            "replication_docs_latency_wt",
            "curr_connections",
            "curr_items",
            "mem_used",
            "ep_meta_data_memory",
            "vb_active_resident_items_ratio",
            "vb_replica_resident_items_ratio",
            "ep_num_value_ejects",
            "ep_tmp_oom_errors",
            "ep_dcp_replica_items_remaining",
            "ep_dcp_replica_total_bytes",
            "ep_dcp_other_items_remaining",
            "ep_dcp_other_total_bytes",
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
            "cpu_utilization_rate",
            "swap_used",
        ]),
        ("fts_stats", [
            "cbft_num_bytes_used_disk",
            "cbft_doc_count",
            "cbft_num_bytes_used_ram",
            "cbft_pct_cpu_gc",
            "cbft_batch_merge_count",
            "cbft_total_gc",
            "cbft_num_bytes_live_data",
            "cbft_total_bytes_indexed",
            "cbft_num_recs_to_persist",
        ]),
        ("fts_query_stats", [
            "cbft_query_slow",
            "cbft_query_timeout",
            "cbft_query_error",
            "cbft_total_term_searchers",
            "cbft_query_total",
            "cbft_total_bytes_query_results",
            "cbft_writer_execute_batch_count",
        ]),
        ("n1ql_stats", [
            "query_avg_req_time",
            "query_avg_svc_time",
            "query_avg_response_size",
            "query_avg_result_count",
            "query_active_requests",
            "query_errors",
            "query_queued_requests",
            "query_request_time",
            "query_requests",
            "query_requests_1000ms",
            "query_requests_250ms",
            "query_requests_5000ms",
            "query_requests_500ms",
            "query_result_count",
            "query_result_size",
            "query_selects",
            "query_service_time",
            "query_warnings",
        ]),
        ("secondary_stats", [
            "index_num_rows_returned",
            "index_scan_bytes_read",
            "index_num_requests",
            "index_num_docs_indexed",
            "index_num_docs_pending",
            "index_fragmentation",
            "index_data_size",
            "index_disk_size",
            "index_total_scan_duration",
            "index_items_count",
        ]),
        ("secondary_debugstats", [
            "num_connections",
            "memory_used_storage",
            "memory_used_queue",
        ]),
        ("secondary_debugstats_bucket", [
            "mutation_queue_size",
            "num_nonalign_ts",
            "ts_queue_size",
        ]),
        ("atop", [
            "sync_gateway_rss",
            "sync_gateway_cpu",
            "beam.smp_rss",
            "beam.smp_cpu",
            "memcached_rss",
            "memcached_cpu",
            "indexer_rss",
            "indexer_cpu",
            "projector_rss",
            "projector_cpu",
            "cbq-engine_rss",
            "cbq-engine_cpu",
            "backup_rss",
            "backup_cpu",
            "cbft_rss",
            "cbft_cpu",
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
            "backup_rbps",
            "backup_wbps",
            "backup_avgqusz",
            "backup_util",
        ]),
        ("net", [
            "in_bytes_per_sec",
            "out_bytes_per_sec",
            "in_packets_per_sec",
            "out_packets_per_sec",
            "ESTABLISHED",
            "TIME_WAIT",
        ]),
    ))

    def __init__(self, snapshots):
        """As part of initialization prefetch list of buckets and servers in
        order to reduce number of SQL queries. Also store list of snapshots.
        """
        self.snapshots = snapshots

        self.buckets = ()
        self.servers = ()
        for snapshot in snapshots:
            buckets = {
                b.name for b in models.Bucket.objects.filter(cluster=snapshot.cluster)
            }
            if self.buckets == ():
                self.buckets = buckets
            else:
                self.buckets = buckets & self.buckets
            servers = {
                s.address for s in models.Server.objects.filter(cluster=snapshot.cluster)
            }
            if self.servers == ():
                self.servers = servers
            else:
                self.servers = servers & self.servers

    def get_all_observables(self):
        """Get all stored in database Observable objects that match provided
        snapshots. There are three expensive queries per snapshot:
        -- get all cluster-wide metrics
        -- get all per-bucket metrics
        -- get all per-server metrics

        That was the only obvious way to achieve O(n) time complexity.

        all_observables is the nested dictionary where every object is may be
        queried as:
            all_observables[bucket/server][cluster][name][collector]

        It's allowed to use "" for bucket names and server addresses.

        Every model object is converted to extended named tuple.
        """
        all_observables = defaultdict(dict)
        for snapshot in self.snapshots:
            # Cluster-wide metrics
            observables = defaultdict(dict)
            for o in models.Observable.objects.filter(cluster=snapshot.cluster,
                                                      bucket__isnull=True,
                                                      server__isnull=True):
                observables[o.collector][o.name] = Observable(
                    snapshot, "", "", o.name, o.collector
                )
            all_observables[""][snapshot.cluster] = observables

            # Per-bucket metrics
            for bucket in self.buckets:
                _bucket = models.Bucket.objects.get(cluster=snapshot.cluster,
                                                    name=bucket)
                observables = defaultdict(dict)
                for o in models.Observable.objects.filter(cluster=snapshot.cluster,
                                                          bucket=_bucket,
                                                          server__isnull=True):
                    observables[o.collector][o.name] = Observable(
                        snapshot, "", bucket, o.name, o.collector
                    )
                all_observables[bucket][snapshot.cluster] = observables

            # Per-server metrics
            for server in self.servers:
                _server = models.Server.objects.get(cluster=snapshot.cluster,
                                                    address=server)
                observables = defaultdict(dict)
                for o in models.Observable.objects.filter(cluster=snapshot.cluster,
                                                          bucket__isnull=True,
                                                          server=_server):
                    observables[o.collector][o.name] = Observable(
                        snapshot, server, "", o.name, o.collector
                    )
                all_observables[server][snapshot.cluster] = observables
        return all_observables

    def __call__(self):
        """Primary class method that return tuple with valid Observable objects
        """
        _all = self.get_all_observables()
        observables = []

        for collector, metrics in self.METRICS.iteritems():
            # Cluster-wide metrics
            if collector in ("active_tasks", "sync_latency", "n1ql_stats",
                             "fts_stats", "fts_query_stats", "fts_latency","secondary_debugstats",):
                for metric in metrics:
                    observables.append([
                        _all[""][snapshot.cluster][collector].get(metric)
                        for snapshot in self.snapshots
                    ])
            # Per-server metrics
            if collector in ("atop", "iostat", "net", "sync_gateway"):
                for metric in metrics:
                    for server in self.servers:
                        observables.append([
                            _all[server][snapshot.cluster][collector].get(metric)
                            for snapshot in self.snapshots
                        ])
            # Per-bucket metrics
            if collector in ("active_tasks", "ns_server",
                             "spring_latency", "spring_query_latency",
                             "durability", "observe",  "xdcr_lag",
                             "secondary_stats", "secondary_debugstats_bucket"):
                for metric in metrics:
                    for bucket in self.buckets:
                        observables.append([
                            _all[bucket][snapshot.cluster][collector].get(metric)
                            for snapshot in self.snapshots
                        ])
        # Skip full mismatch and return tuple with Observable objects
        return tuple(_ for _ in observables if set(_) != {None})
