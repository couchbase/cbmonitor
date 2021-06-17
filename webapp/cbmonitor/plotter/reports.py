from collections import OrderedDict, defaultdict, namedtuple

from cbmonitor import models


Observable = namedtuple(
    "Observable", ["cluster", "server", "bucket", "index", "name", "collector"]
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
        ("sgimport_latency", [
            "sgimport_latency",
        ]),
        ("spring_query_latency", [
            "latency_query",
        ]),
        ("kvstore_stats", [
            "BlockCacheQuota",
            "WriteCacheQuota",
            "BlockCacheMemUsed",
            "BlockCacheHits",
            "BlockCacheMisses",
            "BloomFilterMemUsed",
            "BytesIncoming",
            "BytesOutgoing",
            "BytesPerRead",
            "IndexBlocksSize",
            "MemoryQuota",
            "NCommitBatches",
            "NDeletes",
            "NGets",
            "NReadBytes",
            "NReadBytesCompact",
            "NReadBytesGet",
            "NReadIOs",
            "NReadIOsGet",
            "NSets",
            "NSyncs",
            "NTablesCreated",
            "NTablesDeleted",
            "NTableFiles",
            "TableMetaMemUsed",
            "NFileCountCompacts",
            "NWriteBytes",
            "NWriteBytesCompact",
            "NWriteIOs",
            "ReadAmp",
            "ReadAmpGet",
            "ReadIOAmp",
            "TotalMemUsed",
            "BufferMemUsed",
            "WALMemUsed",
            "WriteAmp",
            "WriteCacheMemUsed",
            "ActiveBloomFilterMemUsed",
            "TotalBlockCacheMemUsed",
            "NCompacts",
            "TxnSizeEstimate",
            "NFlushes",
            "NGetsPerSec",
            "NSetsPerSec",
            "NDeletesPerSec",
            "NCommitBatchesPerSec",
            "NFlushesPerSec",
            "NCompactsPerSec",
            "NSyncsPerSec",
            "NReadBytesPerSec",
            "NReadBytesGetPerSec",
            "NReadBytesCompactPerSec",
            "BytesOutgoingPerSec",
            "NReadIOsPerSec",
            "NReadIOsGetPerSec",
            "BytesIncomingPerSec",
            "NWriteBytesPerSec",
            "NWriteIOsPerSec",
            "NWriteBytesCompactPerSec",
            "RecentWriteAmp",
            "RecentReadAmp",
            "RecentReadAmpGet",
            "RecentReadIOAmp",
            "RecentBytesPerRead",
            "NGetStatsPerSec",
            "NGetStatsComputedPerSec",
            "FlushQueueSize",
            "CompactQueueSize",
            "NBloomFilterHits",
            "NBloomFilterMisses",
            "BloomFilterFPR",
            "NumNormalFlushes",
            "NumPersistentFlushes",
            "NumSyncFlushes",
        ]),
        ("n1ql_stats", [
            "query_requests",
            "query_selects",
            "query_avg_req_time",
            "query_avg_svc_time",
            "query_avg_response_size",
            "query_avg_result_count",
            "query_errors",
            "query_warnings",
            "query_requests_250ms",
            "query_requests_500ms",
            "query_requests_1000ms",
            "query_requests_5000ms",
            "query_invalid_requests",
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
        ("xdcr_stats", [
            "changes_left",
            "percent_completeness",
            "docs_written",
            "docs_filtered",
            "docs_failed_cr_source",
            "rate_replicated",
            "bandwidth_usage",
            "rate_doc_opt_repd",
            "rate_doc_checks",
            "wtavg_meta_latency",
            "wtavg_docs_latency",
        ]),
        ("ns_server_system", [
            "cpu_utilization",
        ]),
        ("ns_server", [
            "ep_dcp_2i_items_sent",
            "ep_dcp_2i_items_remaining",
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
            "curr_connections",
            "curr_items",
            "vb_replica_curr_items",
            "vb_pending_curr_items",
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
            "ep_ops_create",
            "vb_active_ops_create",
            "vb_replica_ops_create",
            "vb_pending_ops_create",
            "ep_ops_update",
            "vb_active_ops_update",
            "vb_replica_ops_update",
            "vb_pending_ops_update",
            "ep_diskqueue_drain",
            "ep_diskqueue_fill",
            "ep_queue_size",
            "avg_bg_wait_time",
            "avg_disk_commit_time",
            "avg_disk_update_time",
            "vb_avg_total_queue_age",
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
        ("analytics", [
            "heap_used",
            "gc_count",
            "gc_time",
            "io_reads",
            "io_writes",
            "system_load_average",
            "disk_used",
            "thread_count",
        ]),
        ("fts_totals", [
            "batch_merge_count",
            "doc_count",
            "iterator_next_count",
            "iterator_seek_count",
            "num_bytes_live_data",
            "num_bytes_used_disk",
            "num_files_on_disk",
            "num_root_memorysegments",
            "num_root_filesegments",
            "num_mutations_to_index",
            "num_pindexes",
            "num_pindexes_actual",
            "num_pindexes_target",
            "num_recs_to_persist",
            "reader_get_count",
            "reader_multi_get_count",
            "reader_prefix_iterator_count",
            "reader_range_iterator_count",
            "timer_batch_store_count",
            "timer_data_delete_count",
            "timer_data_update_count",
            "timer_opaque_get_count",
            "timer_opaque_set_count",
            "timer_rollback_count",
            "timer_snapshot_start_count",
            "total_bytes_indexed",
            "total_bytes_query_results",
            "total_compactions",
            "total_queries",
            "total_queries_error",
            "total_queries_slow",
            "total_queries_timeout",
            "total_request_time",
            "total_term_searchers",
            "writer_execute_batch_count",
            "num_bytes_used_ram",
            "pct_cpu_gc",
            "total_gc",
        ]),
        ("fts_stats", [
            "batch_merge_count",
            "doc_count",
            "iterator_next_count",
            "iterator_seek_count",
            "num_bytes_live_data",
            "num_bytes_used_disk",
            "num_files_on_disk",
            "num_root_memorysegments",
            "num_root_filesegments",
            "num_mutations_to_index",
            "num_pindexes",
            "num_pindexes_actual",
            "num_pindexes_target",
            "num_recs_to_persist",
            "reader_get_count",
            "reader_multi_get_count",
            "reader_prefix_iterator_count",
            "reader_range_iterator_count",
            "timer_batch_store_count",
            "timer_data_delete_count",
            "timer_data_update_count",
            "timer_opaque_get_count",
            "timer_opaque_set_count",
            "timer_rollback_count",
            "timer_snapshot_start_count",
            "total_bytes_indexed",
            "total_bytes_query_results",
            "total_compactions",
            "total_queries",
            "total_queries_error",
            "total_queries_slow",
            "total_queries_timeout",
            "total_request_time",
            "total_term_searchers",
            "writer_execute_batch_count",
            "num_bytes_used_ram",
            "pct_cpu_gc",
            "total_gc",
        ]),
        ("eventing_stats", [
            "DCP_MUTATION",
            "DOC_TIMER_EVENTS",
            "CRON_TIMER_EVENTS",
        ]),
        ("jts_stats", [
            "jts_throughput",
            "jts_latency",
        ]),
        ("eventing_per_node_stats", [
            "DcpEventsRemaining",
        ]),
         ("eventing_per_handler_stats", [
            "on_update_success"
        ]),
        ("eventing_consumer_stats", [
            "eventing_consumer_rss",
            "eventing_consumer_cpu",
        ]),
        ("secondary_stats", [
            "index_items_count",
            "index_num_docs_indexed",
            "index_num_docs_pending",
            "index_num_docs_queued",
            "index_num_requests",
            "index_num_rows_returned",
            "index_scan_bytes_read",
            "index_data_size",
            "index_disk_size",
            "index_fragmentation",
            "index_total_scan_duration",
        ]),
        ("secondaryscan_latency", [
            "Nth-latency",
        ]),
        ("secondary_debugstats", [
            "num_connections",
            "memory_used",
            "memory_used_storage",
            "memory_used_queue",
            "average_indexer_resident_ratio"
        ]),
        ("secondary_debugstats_bucket", [
            "mutation_queue_size",
            "num_nonalign_ts",
            "ts_queue_size",
        ]),
        ("secondary_debugstats_index", [
            "avg_scan_latency",
            "avg_scan_wait_latency",
            "avg_ts_interval",
            "avg_ts_items_count",
            "disk_store_duration",
            "flush_queue_size",
            "num_compactions",
            "num_completed_requests",
            "num_rows_returned",
            "num_rows_scanned_aggr",
            "scan_cache_hit_aggr",
            "timings_dcp_getseqs",
            "timings_storage_commit",
            "timings_storage_del",
            "timings_storage_get",
            "timings_storage_set",
            "timings_storage_snapshot_create",
        ]),
        ("secondary_storage_stats", [
            "MainStore_memory_size",
            "MainStore_num_cached_pages",
            "MainStore_num_pages",
            "MainStore_num_pages_swapout",
            "MainStore_num_pages_swapin",
            "MainStore_bytes_incoming",
            "MainStore_bytes_written",
            "MainStore_write_amp",
            "MainStore_lss_fragmentation",
            "MainStore_cache_hits",
            "MainStore_cache_misses",
            "MainStore_cache_hit_ratio",
            "MainStore_rcache_hits",
            "MainStore_rcache_misses",
            "MainStore_rcache_hit_ratio",
            "MainStore_resident_ratio",
            "MainStore_allocated",
            "MainStore_freed",
            "MainStore_reclaimed",
            "MainStore_reclaim_pending",
            "MainStore_mvcc_purge_ratio",
            "MainStore_memory_quota",
            "MainStore_lss_blk_read_bs",
            "MainStore_lss_blk_gc_reads_bs",
            "MainStore_lss_blk_rdr_reads_bs",
            "BackStore_memory_size",
            "BackStore_num_cached_pages",
            "BackStore_num_pages",
            "BackStore_num_pages_swapout",
            "BackStore_num_pages_swapin",
            "BackStore_bytes_incoming",
            "BackStore_bytes_written",
            "BackStore_write_amp",
            "BackStore_lss_fragmentation",
            "BackStore_cache_hits",
            "BackStore_cache_misses",
            "BackStore_cache_hit_ratio",
            "BackStore_rcache_hits",
            "BackStore_rcache_misses",
            "BackStore_rcache_hit_ratio",
            "BackStore_resident_ratio",
            "BackStore_allocated",
            "BackStore_freed",
            "BackStore_reclaimed",
            "BackStore_reclaim_pending",
            "BackStore_mvcc_purge_ratio",
            "BackStore_lss_blk_read_bs",
            "BackStore_lss_blk_gc_reads_bs",
            "BackStore_lss_blk_rdr_reads_bs",
        ]),
        ("secondary_storage_stats_mm", [
            "mm_allocated",
            "mm_resident",
            "mm_metadata",
        ]),
        ("atop", [
            "cbindex_cpu",
            "cbindex_rss",
            "cbindexperf_cpu",
            "cbindexperf_rss",
            "dcptest_rss",
            "dcptest_cpu",
            "cbbackupmgr_rss",
            "cbbackupmgr_cpu",
            "cbexport_rss",
            "cbexport_cpu",
            "cbimport_rss",
            "cbimport_cpu",
            "beam.smp_rss",
            "beam.smp_cpu",
            "memcached_rss",
            "memcached_cpu",
            "goxdcr_rss",
            "goxdcr_cpu",
            "indexer_rss",
            "indexer_cpu",
            "projector_rss",
            "projector_cpu",
            "cbq-engine_rss",
            "cbq-engine_cpu",
            "cbft_rss",
            "cbft_cpu",
            "eventing-produc_rss",
            "eventing-produc_cpu",
            "sync_gateway_cpu",
            "sync_gateway_rss",
            "sync_gateway_vsize",
            "java_rss",
            "java_cpu",
            "cbc-pillowfight_rss",
            "cbc-pillowfight_cpu",
            "cblite_cpu",
            "cblite_rss",
            "cblite_vsize",
            "prometheus_rss",
            "prometheus_cpu",
        ]),
        ("sysdig", [
            "indexer_pread",
            "indexer_pwrite",
            "memcached_pread",
            "memcached_pwrite",
        ]),
        ("iostat", [
            "tools_rbps",
            "tools_wbps",
            "tools_avgqusz",
            "tools_util",
            "data_rps",
            "data_wps",
            "data_rbps",
            "data_wbps",
            "data_avgqusz",
            "data_util",
            "index_rbps",
            "index_wbps",
            "index_avgqusz",
            "index_util",
            "analytics0_rbps",
            "analytics0_wbps",
            "analytics0_util",
            "analytics1_rbps",
            "analytics1_wbps",
            "analytics1_util",
            "analytics2_rbps",
            "analytics2_wbps",
            "analytics2_util",
            "analytics3_rbps",
            "analytics3_wbps",
            "analytics3_util",
            "analytics4_rbps",
            "analytics4_wbps",
            "analytics4_util",
        ]),
        ("disk", [
            "data_bytes_read",
            "data_bytes_written",
        ]),
        ("meminfo", [
            "MemFree",
            "Dirty",
            "Buffers",
            "Cached",
            "SUnreclaim",
        ]),
        ("pcstat", [
            "page_cache_hit_ratio",
            "page_cache_total_hits",
            "data_avg_page_cache_rr",
        ]),
        ("net", [
            "in_bytes_per_sec",
            "out_bytes_per_sec",
            "ESTABLISHED",
            "TIME_WAIT",
        ]),
        ("vmstat", [
            "allocstall",
        ]),
        ("syncgateway_node_stats", [
            "syncgateway__global__resource_utilization__process_cpu_percent_utilization",
            "syncgateway__global__resource_utilization__process_memory_resident",
            "syncgateway__global__resource_utilization__system_memory_total",
            "syncgateway__global__resource_utilization__pub_net_bytes_sent",
            "syncgateway__global__resource_utilization__pub_net_bytes_recv",
            "syncgateway__global__resource_utilization__admin_net_bytes_sent",
            "syncgateway__global__resource_utilization__admin_net_bytes_recv",
            "syncgateway__global__resource_utilization__num_goroutines",
            "syncgateway__global__resource_utilization__goroutines_high_watermark",
            "syncgateway__global__resource_utilization__go_memstats_sys",
            "syncgateway__global__resource_utilization__go_memstats_heapalloc",
            "syncgateway__global__resource_utilization__go_memstats_heapidle",
            "syncgateway__global__resource_utilization__go_memstats_heapinuse",
            "syncgateway__global__resource_utilization__go_memstats_heapreleased",
            "syncgateway__global__resource_utilization__go_memstats_stackinuse",
            "syncgateway__global__resource_utilization__go_memstats_stacksys",
            "syncgateway__global__resource_utilization__go_memstats_pausetotalns",
            "syncgateway__global__resource_utilization__error_count",
            "syncgateway__global__resource_utilization__warn_count",
            "syncgateway__per_db__db__cache__rev_cache_hits",
            "syncgateway__per_db__db__cache__rev_cache_misses",
            "syncgateway__per_db__db__cache__rev_cache_bypass",
            "syncgateway__per_db__db__cache__chan_cache_hits",
            "syncgateway__per_db__db__cache__chan_cache_misses",
            "syncgateway__per_db__db__cache__chan_cache_active_revs",
            "syncgateway__per_db__db__cache__chan_cache_tombstone_revs",
            "syncgateway__per_db__db__cache__chan_cache_removal_revs",
            "syncgateway__per_db__db__cache__chan_cache_num_channels",
            "syncgateway__per_db__db__cache__chan_cache_max_entries",
            "syncgateway__per_db__db__cache__chan_cache_pending_queries",
            "syncgateway__per_db__db__cache__chan_cache_channels_added",
            "syncgateway__per_db__db__cache__chan_cache_channels_evicted_inactive",
            "syncgateway__per_db__db__cache__chan_cache_channels_evicted_nru",
            "syncgateway__per_db__db__cache__chan_cache_compact_count",
            "syncgateway__per_db__db__cache__chan_cache_compact_time",
            "syncgateway__per_db__db__cache__num_active_channels",
            "syncgateway__per_db__db__cache__num_skipped_seqs",
            "syncgateway__per_db__db__cache__abandoned_seqs",
            "syncgateway__per_db__db__cache__high_seq_cached",
            "syncgateway__per_db__db__cache__high_seq_stable",
            "syncgateway__per_db__db__cache__skipped_seq_len",
            "syncgateway__per_db__db__cache__pending_seq_len",
            "syncgateway__per_db__db__database__sequence_get_count",
            "syncgateway__per_db__db__database__sequence_incr_count",
            "syncgateway__per_db__db__database__sequence_reserved_count",
            "syncgateway__per_db__db__database__sequence_assigned_count",
            "syncgateway__per_db__db__database__sequence_released_count",
            "syncgateway__per_db__db__database__crc32c_match_count",
            "syncgateway__per_db__db__database__num_replications_active",
            "syncgateway__per_db__db__database__num_replications_total",
            "syncgateway__per_db__db__database__num_doc_writes",
            "syncgateway__per_db__db__database__num_tombstones_compacted",
            "syncgateway__per_db__db__database__doc_writes_bytes",
            "syncgateway__per_db__db__database__doc_writes_xattr_bytes",
            "syncgateway__per_db__db__database__num_doc_reads_rest",
            "syncgateway__per_db__db__database__num_doc_reads_blip",
            "syncgateway__per_db__db__database__doc_writes_bytes_blip",
            "syncgateway__per_db__db__database__doc_reads_bytes_blip",
            "syncgateway__per_db__db__database__warn_xattr_size_count",
            "syncgateway__per_db__db__database__warn_channels_per_doc_count",
            "syncgateway__per_db__db__database__warn_grants_per_doc_count",
            "syncgateway__per_db__db__database__dcp_received_count",
            "syncgateway__per_db__db__database__high_seq_feed",
            "syncgateway__per_db__db__database__dcp_received_time",
            "syncgateway__per_db__db__database__dcp_caching_count",
            "syncgateway__per_db__db__database__dcp_caching_time",
            "syncgateway__per_db__db__delta_sync__deltas_requested",
            "syncgateway__per_db__db__delta_sync__deltas_sent",
            "syncgateway__per_db__db__delta_sync__delta_pull_replication_count",
            "syncgateway__per_db__db__delta_sync__delta_cache_hit",
            "syncgateway__per_db__db__delta_sync__delta_cache_miss",
            "syncgateway__per_db__db__delta_sync__delta_push_doc_count",
            "syncgateway__per_db__db__shared_bucket_import__import_count",
            "syncgateway__per_db__db__shared_bucket_import__import_cancel_cas",
            "syncgateway__per_db__db__shared_bucket_import__import_error_count",
            "syncgateway__per_db__db__shared_bucket_import__import_processing_time",
            "syncgateway__per_db__db__cbl_replication_push__doc_push_count",
            "syncgateway__per_db__db__cbl_replication_push__write_processing_time",
            "syncgateway__per_db__db__cbl_replication_push__sync_function_time",
            "syncgateway__per_db__db__cbl_replication_push__sync_function_count",
            "syncgateway__per_db__db__cbl_replication_push__propose_change_time",
            "syncgateway__per_db__db__cbl_replication_push__propose_change_count",
            "syncgateway__per_db__db__cbl_replication_push__attachment_push_count",
            "syncgateway__per_db__db__cbl_replication_push__attachment_push_bytes",
            "syncgateway__per_db__db__cbl_replication_push__conflict_write_count",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_active_one_shot",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_active_continuous",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_total_one_shot",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_total_continuous",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_since_zero",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_caught_up",
            "syncgateway__per_db__db__cbl_replication_pull__request_changes_count",
            "syncgateway__per_db__db__cbl_replication_pull__request_changes_time",
            "syncgateway__per_db__db__cbl_replication_pull__rev_send_count",
            "syncgateway__per_db__db__cbl_replication_pull__rev_send_latency",
            "syncgateway__per_db__db__cbl_replication_pull__rev_processing_time",
            "syncgateway__per_db__db__cbl_replication_pull__max_pending",
            "syncgateway__per_db__db__cbl_replication_pull__attachment_pull_count",
            "syncgateway__per_db__db__cbl_replication_pull__attachment_pull_bytes",
            "syncgateway__per_db__db__security__num_docs_rejected",
            "syncgateway__per_db__db__security__num_access_errors",
            "syncgateway__per_db__db__security__auth_success_count",
            "syncgateway__per_db__db__security__auth_failed_count",
            "syncgateway__per_db__db__security__total_auth_time",
            "syncGateway_import__import_count",
            "syncgateway__per_db__db__gsi_views__access_count",
            "syncgateway__per_db__db__gsi_views__roleAccess_count",
            "syncgateway__per_db__db__gsi_views__channels_count",
        ]),
        ("syncgateway_cluster_stats", [
            "syncgateway__global__resource_utilization__process_cpu_percent_utilization",
            "syncgateway__global__resource_utilization__process_memory_resident",
            "syncgateway__global__resource_utilization__system_memory_total",
            "syncgateway__global__resource_utilization__pub_net_bytes_sent",
            "syncgateway__global__resource_utilization__pub_net_bytes_recv",
            "syncgateway__global__resource_utilization__admin_net_bytes_sent",
            "syncgateway__global__resource_utilization__admin_net_bytes_recv",
            "syncgateway__global__resource_utilization__num_goroutines",
            "syncgateway__global__resource_utilization__goroutines_high_watermark",
            "syncgateway__global__resource_utilization__go_memstats_sys",
            "syncgateway__global__resource_utilization__go_memstats_heapalloc",
            "syncgateway__global__resource_utilization__go_memstats_heapidle",
            "syncgateway__global__resource_utilization__go_memstats_heapinuse",
            "syncgateway__global__resource_utilization__go_memstats_heapreleased",
            "syncgateway__global__resource_utilization__go_memstats_stackinuse",
            "syncgateway__global__resource_utilization__go_memstats_stacksys",
            "syncgateway__global__resource_utilization__go_memstats_pausetotalns",
            "syncgateway__global__resource_utilization__error_count",
            "syncgateway__global__resource_utilization__warn_count",
            "syncgateway__per_db__db__cache__rev_cache_hits",
            "syncgateway__per_db__db__cache__rev_cache_misses",
            "syncgateway__per_db__db__cache__rev_cache_bypass",
            "syncgateway__per_db__db__cache__chan_cache_hits",
            "syncgateway__per_db__db__cache__chan_cache_misses",
            "syncgateway__per_db__db__cache__chan_cache_active_revs",
            "syncgateway__per_db__db__cache__chan_cache_tombstone_revs",
            "syncgateway__per_db__db__cache__chan_cache_removal_revs",
            "syncgateway__per_db__db__cache__chan_cache_num_channels",
            "syncgateway__per_db__db__cache__chan_cache_max_entries",
            "syncgateway__per_db__db__cache__chan_cache_pending_queries",
            "syncgateway__per_db__db__cache__chan_cache_channels_added",
            "syncgateway__per_db__db__cache__chan_cache_channels_evicted_inactive",
            "syncgateway__per_db__db__cache__chan_cache_channels_evicted_nru",
            "syncgateway__per_db__db__cache__chan_cache_compact_count",
            "syncgateway__per_db__db__cache__chan_cache_compact_time",
            "syncgateway__per_db__db__cache__num_active_channels",
            "syncgateway__per_db__db__cache__num_skipped_seqs",
            "syncgateway__per_db__db__cache__abandoned_seqs",
            "syncgateway__per_db__db__cache__high_seq_cached",
            "syncgateway__per_db__db__cache__high_seq_stable",
            "syncgateway__per_db__db__cache__skipped_seq_len",
            "syncgateway__per_db__db__cache__pending_seq_len",
            "syncgateway__per_db__db__database__sequence_get_count",
            "syncgateway__per_db__db__database__sequence_incr_count",
            "syncgateway__per_db__db__database__sequence_reserved_count",
            "syncgateway__per_db__db__database__sequence_assigned_count",
            "syncgateway__per_db__db__database__sequence_released_count",
            "syncgateway__per_db__db__database__crc32c_match_count",
            "syncgateway__per_db__db__database__num_replications_active",
            "syncgateway__per_db__db__database__num_replications_total",
            "syncgateway__per_db__db__database__num_doc_writes",
            "syncgateway__per_db__db__database__num_tombstones_compacted",
            "syncgateway__per_db__db__database__doc_writes_bytes",
            "syncgateway__per_db__db__database__doc_writes_xattr_bytes",
            "syncgateway__per_db__db__database__num_doc_reads_rest",
            "syncgateway__per_db__db__database__num_doc_reads_blip",
            "syncgateway__per_db__db__database__doc_writes_bytes_blip",
            "syncgateway__per_db__db__database__doc_reads_bytes_blip",
            "syncgateway__per_db__db__database__warn_xattr_size_count",
            "syncgateway__per_db__db__database__warn_channels_per_doc_count",
            "syncgateway__per_db__db__database__warn_grants_per_doc_count",
            "syncgateway__per_db__db__database__dcp_received_count",
            "syncgateway__per_db__db__database__high_seq_feed",
            "syncgateway__per_db__db__database__dcp_received_time",
            "syncgateway__per_db__db__database__dcp_caching_count",
            "syncgateway__per_db__db__database__dcp_caching_time",
            "syncgateway__per_db__db__delta_sync__deltas_requested",
            "syncgateway__per_db__db__delta_sync__deltas_sent",
            "syncgateway__per_db__db__delta_sync__delta_pull_replication_count",
            "syncgateway__per_db__db__delta_sync__delta_cache_hit",
            "syncgateway__per_db__db__delta_sync__delta_cache_miss",
            "syncgateway__per_db__db__delta_sync__delta_push_doc_count",
            "syncgateway__per_db__db__shared_bucket_import__import_count",
            "syncgateway__per_db__db__shared_bucket_import__import_cancel_cas",
            "syncgateway__per_db__db__shared_bucket_import__import_error_count",
            "syncgateway__per_db__db__shared_bucket_import__import_processing_time",
            "syncgateway__per_db__db__cbl_replication_push__doc_push_count",
            "syncgateway__per_db__db__cbl_replication_push__write_processing_time",
            "syncgateway__per_db__db__cbl_replication_push__sync_function_time",
            "syncgateway__per_db__db__cbl_replication_push__sync_function_count",
            "syncgateway__per_db__db__cbl_replication_push__propose_change_time",
            "syncgateway__per_db__db__cbl_replication_push__propose_change_count",
            "syncgateway__per_db__db__cbl_replication_push__attachment_push_count",
            "syncgateway__per_db__db__cbl_replication_push__attachment_push_bytes",
            "syncgateway__per_db__db__cbl_replication_push__conflict_write_count",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_active_one_shot",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_active_continuous",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_total_one_shot",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_total_continuous",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_since_zero",
            "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_caught_up",
            "syncgateway__per_db__db__cbl_replication_pull__request_changes_count",
            "syncgateway__per_db__db__cbl_replication_pull__request_changes_time",
            "syncgateway__per_db__db__cbl_replication_pull__rev_send_count",
            "syncgateway__per_db__db__cbl_replication_pull__rev_send_latency",
            "syncgateway__per_db__db__cbl_replication_pull__rev_processing_time",
            "syncgateway__per_db__db__cbl_replication_pull__max_pending",
            "syncgateway__per_db__db__cbl_replication_pull__attachment_pull_count",
            "syncgateway__per_db__db__cbl_replication_pull__attachment_pull_bytes",
            "syncgateway__per_db__db__security__num_docs_rejected",
            "syncgateway__per_db__db__security__num_access_errors",
            "syncgateway__per_db__db__security__auth_success_count",
            "syncgateway__per_db__db__security__auth_failed_count",
            "syncgateway__per_db__db__security__total_auth_time",
            "syncGateway_import__import_count",
            "syncgateway__per_db__db__gsi_views__access_count",
            "syncgateway__per_db__db__gsi_views__roleAccess_count",
            "syncgateway__per_db__db__gsi_views__channels_count",
        ]),
    ))

    def __init__(self, snapshots):
        """As part of initialization prefetch list of buckets and servers in
        order to reduce number of SQL queries. Also store list of snapshots.
        """
        self.snapshots = snapshots

        self.buckets = ()
        self.servers = ()
        self.indexes = ()
        for snapshot in snapshots:
            buckets = {
                b.name for b in models.Bucket.objects.filter(cluster=snapshot.cluster)
            }
            if self.buckets == ():
                self.buckets = buckets
            else:
                self.buckets = buckets & self.buckets

            indexes = {
                i.name for i in models.Index.objects.filter(cluster=snapshot.cluster)
            }
            if self.indexes == ():
                self.indexes = indexes
            else:
                self.indexes = indexes & self.indexes

            servers = {
                s.address for s in models.Server.objects.filter(cluster=snapshot.cluster)
            }
            if self.servers == ():
                self.servers = servers
            else:
                self.servers = servers & self.servers

    def get_observables(self):
        """Get all stored in database Observable objects that match provided
        snapshots. There are three expensive queries per snapshot:
        -- get all cluster-wide metrics
        -- get all per-bucket metrics
        -- get all per-index metrics
        -- get all per-server metrics

        That was the only obvious way to achieve O(n) time complexity.

        all_observables is the nested dictionary where every object is may be
        queried as:
            all_observables[bucket/server/index][cluster][name][collector]

        It's allowed to use "" for bucket names and server addresses.

        Every model object is converted to extended named tuple.
        """
        all_observables = defaultdict(dict)
        all_observables[""] = defaultdict(dict)
        for snapshot in self.snapshots:
            # Cluster-wide metrics
            observables = defaultdict(dict)
            for o in models.Observable.objects.filter(cluster=snapshot.cluster,
                                                      bucket__isnull=True,
                                                      server__isnull=True,
                                                      index__isnull=True):

                observables[o.collector][o.name] = Observable(
                    snapshot.cluster.name, "", "", "", o.name, o.collector
                )
            all_observables[""][""][snapshot.cluster] = observables

            # Per-bucket metrics
            for bucket in self.buckets:
                _bucket = models.Bucket.objects.get(cluster=snapshot.cluster,
                                                    name=bucket)
                observables = defaultdict(dict)
                for o in models.Observable.objects.filter(cluster=snapshot.cluster,
                                                          bucket=_bucket,
                                                          server__isnull=True,
                                                          index__isnull=True):
                    observables[o.collector][o.name] = Observable(
                        snapshot.cluster.name, "", bucket, "", o.name, o.collector
                    )
                all_observables[""][bucket][snapshot.cluster] = observables

            # Per-index metrics
            for index in self.indexes:
                _index = models.Index.objects.get(cluster=snapshot.cluster,
                                                  name=index)
                observables = defaultdict(dict)
                for o in models.Observable.objects.filter(cluster=snapshot.cluster,
                                                          bucket__isnull=True,
                                                          server__isnull=True,
                                                          index=_index):
                    observables[o.collector][o.name] = Observable(
                        snapshot.cluster.name, "", "", index, o.name, o.collector
                    )
                all_observables[""][index][snapshot.cluster] = observables

            # Per-server metrics
            for server in self.servers:
                _server = models.Server.objects.get(cluster=snapshot.cluster,
                                                    address=server)
                observables = defaultdict(dict)
                for o in models.Observable.objects.filter(cluster=snapshot.cluster,
                                                          bucket__isnull=True,
                                                          server=_server,
                                                          index__isnull=True):
                    observables[o.collector][o.name] = Observable(
                        snapshot.cluster.name, server, "", "", o.name, o.collector
                    )
                all_observables[""][server][snapshot.cluster] = observables

            # Per-server Per-Bucket metrics
            for server in self.servers:
                if server not in all_observables:
                    all_observables[server] = defaultdict(dict)
                for bucket in self.buckets:
                    _server = models.Server.objects.get(cluster=snapshot.cluster,
                                                        address=server)
                    _bucket = models.Bucket.objects.get(cluster=snapshot.cluster,
                                                        name=bucket)
                    observables = defaultdict(dict)
                    for o in models.Observable.objects.filter(cluster=snapshot.cluster,
                                                              bucket=_bucket,
                                                              server=_server,
                                                              index__isnull=True):
                        observables[o.collector][o.name] = Observable(
                            snapshot.cluster.name, server, bucket, "", o.name, o.collector
                        )
                    all_observables[server][bucket][snapshot.cluster] = observables

        return all_observables

    def get_report(self):
        """Primary class method that return tuple with valid Observable objects
        """
        all_observables = self.get_observables()

        observables = []

        for collector, metrics in self.METRICS.iteritems():
            # Cluster-wide metrics
            if collector in ("active_tasks",
                             "ns_server",
                             "n1ql_stats",
                             "fts_totals",
                             "fts_latency",
                             "secondary_debugstats",
                             "secondaryscan_latency",
                             "secondary_storage_stats_mm",
                             "syncgateway_cluster_stats",
                             "sgimport_latency",
                             ):
                for metric in metrics:
                    observables.append([
                        all_observables[""][""][snapshot.cluster][collector].get(metric)
                        for snapshot in self.snapshots
                    ])
            # Per-server metrics
            if collector in ("atop",
                             "analytics",
                             "disk",
                             "iostat",
                             "net",
                             "fts_stats",
                             "meminfo",
                             "pcstat",
                             "sysdig",
                             "ns_server_system",
                             "syncgateway_node_stats",
                             "eventing_per_node_stats",
                             "sgimport_latency",
                             "vmstat",
                             ):
                for metric in metrics:
                    for server in self.servers:
                        observables.append([
                            all_observables[""][server][snapshot.cluster][collector].get(metric)
                            for snapshot in self.snapshots
                        ])
            # Per-bucket metrics
            if collector in ("active_tasks",
                             "xdcr_stats",
                             "ns_server",
                             "spring_latency",
                             "spring_query_latency",
                             "durability",
                             "observe",
                             "xdcr_lag",
                             "secondary_stats",
                             "secondary_debugstats_bucket",
                             "eventing_stats",
                             "jts_stats",
                             "sgimport_latency",
                             "kvstore_stats",
                             "eventing_per_handler_stats",
                             ):
                for metric in metrics:
                    for bucket in self.buckets:
                        observables.append([
                            all_observables[""][bucket][snapshot.cluster][collector].get(metric)
                            for snapshot in self.snapshots
                        ])
            # Per-index metrics
            if collector in ("secondary_debugstats_index",
                             "secondary_storage_stats",
                             ):
                for metric in metrics:
                    for index in self.indexes:
                        observables.append([
                            all_observables[""][index][snapshot.cluster][collector].get(metric)
                            for snapshot in self.snapshots
                        ])
            # Per-server, Per-bucket metrics
            if collector in ("eventing_consumer_stats",
                             ):
                for metric in metrics:
                    for server in self.servers:
                        for bucket in self.buckets:
                            if bucket in all_observables[server]:
                                observables.append([
                                    all_observables[server][bucket][snapshot.cluster][collector].get(metric)
                                    for snapshot in self.snapshots
                                    if snapshot.cluster in all_observables[server][bucket]
                                ])

        # Skip full mismatch and return tuple with Observable objects
        return tuple(_ for _ in observables if set(_) != {None})
