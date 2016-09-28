LABELS = {
    "rebalance_progress": "Rebalance progress, %",
    "ops": "Ops per sec",
    "cmd_get": "GET ops per sec",
    "cmd_set": "SET ops per sec",
    "delete_hits": "DELETE ops per sec",
    "cas_hits": "CAS ops per sec",
    "curr_connections": "Connections",
    "hibernated_waked": "Streaming requests wakeups per sec",
    "curr_items": "Active items",
    "mem_used": "Memory used, bytes",
    "ep_meta_data_memory": "Metadata in RAM, bytes",
    "vb_active_resident_items_ratio": "Active docs resident, %",
    "vb_replica_resident_items_ratio": "Replica docs resident, %",
    "ep_num_value_ejects": "Ejections per sec",
    "ep_dcp_2i_items_sent": "DCP 2i items sent, items",
    "ep_dcp_2i_items_remaining": "DCP 2i items remaining, items",
    "ep_dcp_replica_items_remaining": "DCP replication backlog, items",
    "ep_dcp_replica_total_bytes": "DCP replication bytes sent, bytes",
    "ep_dcp_other_items_remaining": "DCP clients backlog, items",
    "ep_dcp_other_total_bytes": "DCP clients bytes sent, bytes",
    "disk_write_queue": "Disk write queue, items",
    "ep_cache_miss_rate": "Cache miss ratio, %",
    "ep_bg_fetched": "Disk reads per sec",
    "ep_ops_create": "Disk creates per sec",
    "ep_ops_update": "Disk updates per sec",
    "ep_diskqueue_drain": "Drain rate, items/sec",
    "avg_bg_wait_time": "BgFetcher wait time, us",
    "avg_disk_commit_time": "Disk commit time, s",
    "avg_disk_update_time": "Disk update time, us",
    "vb_avg_total_queue_age": "Average age of all items in the disk write queue, sec",
    "couch_docs_data_size": "Docs data size, bytes",
    "couch_docs_actual_disk_size": "Docs total disk size, bytes",
    "couch_docs_fragmentation": "Docs fragmentation, %",
    "couch_total_disk_size": "Total disk size, bytes",
    "changes_left": "Outbound XDCR mutations, items",
    "percent_completeness": "Percentage of checked items out of all checked and to-be-replicated items",
    "docs_written": "Number of mutations that have been replicated to other clusters",
    "docs_filtered": "Number of mutations per second that have been filtered out",
    "docs_failed_cr_source": "Number of mutations that failed conflict resolution",
    "rate_replicated": "Number of replicated mutations per second",
    "bandwidth_usage": "Rate of replication, bytes/sec",
    "rate_doc_opt_repd": "Number of optimistically replicated mutations per second",
    "rate_doc_checks": "Number of doc checks per second",
    "wtavg_meta_latency": "Latency of sending getMeta and waiting for conflict solution, ms",
    "wtavg_docs_latency": "Latency of sending replicated mutations to remote cluster, ms",
    "xdc_ops": "Total XDCR operations per sec",
    "ep_num_ops_get_meta": "Metadata reads per sec",
    "ep_num_ops_set_meta": "Metadata sets per sec",
    "ep_num_ops_del_meta": "Metadata deletes per sec",
    "couch_views_ops": "View reads per sec",
    "couch_views_data_size": "Views data size, bytes",
    "couch_views_actual_disk_size": "Views total disk size, bytes",
    "couch_views_fragmentation": "Views fragmentation, %",
    "cpu_utilization_rate": "CPU utilization across all cores in cluster, %",
    "swap_used": "Swap space in use across all servers in cluster, bytes",
    "beam.smp_rss": "beam.smp resident set size, bytes",
    "beam.smp_cpu": "beam.smp CPU utilization, %",
    "goxdcr_rss": "goxdcr resident set size, bytes",
    "goxdcr_cpu": "goxdcr CPU utilization, %",
    "memcached_rss": "memcached resident set size, bytes",
    "memcached_cpu": "memcached CPU utilization, %",
    "indexer_rss": "indexer resident set size, bytes",
    "indexer_cpu": "indexer CPU utilization, %",
    "projector_rss": "projector resident set size, bytes",
    "projector_cpu": "projector CPU utilization, %",
    "cbq-engine_rss": "cbq-engine resident set size, bytes",
    "cbq-engine_cpu": "cbq-engine CPU utilization, %",
    "cbft_rss": "FTS resident set size, bytes",
    "cbft_cpu": "FTS CPU utilization, %",
    "xdcr_lag": "Total XDCR lag (from memory to memory), ms",
    "xdcr_persistence_time": "Observe latency, ms",
    "xdcr_diff": "Replication lag, ms",
    "latency_set": "SET ops latency, ms",
    "latency_get": "GET ops latency, ms",
    "latency_query": "Query latency, ms",
    "latency_observe": "OBSERVE latency, ms",
    "latency_persist_to": "persistTo=1 latency, ms",
    "latency_replicate_to": "replicateTo=1 latency, ms",
    "data_rbps": "Bytes read/sec",
    "data_wbps": "Bytes written/sec",
    "data_avgqusz": "The average queue length",
    "data_util": "Disk bandwidth utilization, %",
    "index_rbps": "Bytes read/sec",
    "index_wbps": "Bytes written/sec",
    "index_avgqusz": "The average queue length",
    "index_util": "Disk bandwidth utilization, %",
    "bucket_compaction_progress": "Compaction progress, %",
    "in_bytes_per_sec": "Incoming bytes/sec",
    "out_bytes_per_sec": "Outgoing bytes/sec",
    "in_packets_per_sec": "Incoming packets/sec",
    "out_packets_per_sec": "Outgoing packets/sec",
    "ESTABLISHED": "Connections in ESTABLISHED state",
    "TIME_WAIT": "Connections in TIME_WAIT state",
    "index_num_rows_returned": "Number of rows returned by 2i",
    "index_scan_bytes_read": "Bytes read by 2i scans",
    "index_num_requests": "Number of 2i requests",
    "index_num_docs_indexed": "Number of documents indexed in 2i",
    "index_num_docs_pending": "Number of remaining documents to be indexed",
    "index_fragmentation": "fragmentation in secondary indexing",
    "index_data_size": "2i data size",
    "index_disk_size": "2i size on disk",
    "index_total_scan_duration": "total time spent by 2i on scans",
    "index_items_count": "number of items in 2i",
    "num_connections": "Number of connections to index node",
    "memory_used_storage": "Memory used for storage, index node, bytes",
    "memory_used_queue": "Memory used for queue on index node, bytes",
    "mutation_queue_size": "Mutation queue size on index node, items",
    "num_nonalign_ts": "Number of non align ts on index node, snapshots",
    "ts_queue_size": "ts queue size on index node, snapshots",
    "avg_scan_latency": "Average scan latency, ns",
    "avg_ts_interval": "Average ts interval, ns",
    "num_completed_requests": "Number of completed requests",
    "avg_ts_items_count": "Average ts items count, items",
    "num_compactions": "Number of compactions",
    "num_rows_returned": "Number of rows returned",
    "flush_queue_size": "Flush queue size, items",
    "avg_scan_wait_latency": "Average scan wait latency, ns",
    "timings_storage_commit": "Average timings storage commit, ns",
    "timings_storage_del": "Average timings storage del, ns",
    "timings_storage_get": "Average timings storage get, ns",
    "timings_storage_set": "Average timings storage set, ns",
    "timings_storage_snapshot_create": "Average timings storage snapshot create, ns",
    "timings_dcp_getseqs": "Average timings dcp get seq, ns",
    "query_requests": "Number of N1QL requests processed per sec",
    "query_selects": "Number of N1QL selects processed per sec",
    "query_avg_req_time": "Average end-to-end time to process a query, sec",
    "query_avg_svc_time": "Average time to execute a query, sec",
    "query_avg_response_size": "Average size of the data returned by a query, bytes",
    "query_avg_result_count": "Average number of results (documents) returned by a query",
    "query_errors": "Number of N1QL errors returned per sec",
    "query_warnings": "Number of N1QL errors returned per sec",
    "query_requests_250ms": "Number of queries that take longer than 250ms per sec",
    "query_requests_500ms": "Number of queries that take longer than 500ms per sec",
    "query_requests_1000ms": "Number of queries that take longer than 1000ms per sec",
    "query_requests_5000ms": "Number of queries that take longer than 5000ms per sec",
    "query_invalid_requests": "Number of requests for unsupported endpoints per sec",
    "cbft_num_bytes_used_disk": "FTS index size on disk in GB ",
    "cbft_doc_count": "FTS indexing rate",
    "cbft_num_bytes_used_ram": "FTS ram used by cbft process",
    "cbft_pct_cpu_gc": "FTS garbage collection CPU usage",
    "cbft_query_slow": "FTS slow query",
    "cbft_query_timeout": "FTS timeout query",
    "cbft_query_error": "FTS error query",
    "cbft_batch_merge_count":"FTS batch merge_count ",
    "cbft_total_gc" : "FTS garbage collector count",
    "cbft_num_bytes_live_data": "FTS live data size",
    "cbft_total_term_searchers": "FTS total term search ",
    "cbft_query_total" : "FTS total queries",
    "cbft_total_bytes_query_results": "FTS total query bytes",
    "cbft_writer_execute_batch_count": "FTS writer batch count",
    "cbft_latency_get": "FTS latency in ms",
    "cbft_avg_queries_latency": "FTS average queries latency (server)",
    "elastic_latency_get": "ElasticSearch latency in ms",
    "cbft_total_bytes_indexed": "FTS total index size",
    "cbft_num_recs_to_persist": "FTS number of records in queue",
    "elastic_cache_hit": "Elasticsearch query cache hit",
    "elastic_cache_size": "Elasticsearch query cache size",
    "elastic_filter_cache_size": "Elasticsearch filter cache size",
    "elastic_active_search": "Elasticsearch active search",
    "elastic_query_total": "Elasticsearch total query",
}

HISTOGRAMS = (
    "latency_get",
    "latency_set",
    "latency_query",
    "latency_observe",
    "latency_persist_to",
    "latency_replicate_to",
    "xdcr_lag",
    "xdcr_persistence_time",
    "xdcr_diff",
    "replication_meta_latency_wt",
    "replication_docs_latency_wt",
    "avg_bg_wait_time",
    "avg_disk_commit_time",
    "avg_disk_update_time",
    "query_avg_req_time",
    "query_avg_svc_time",
    "cbft_latency_get",
    "elastic_latency_get",
)

ZOOM_HISTOGRAMS = (
    "latency_get",
    "latency_set",
    "latency_query",
    "avg_bg_wait_time",
    "cbft_latency_get",
    "elastic_latency_get",
)

KDE = (
    "latency_query",
    "latency_get",
    "latency_set",
    "xdcr_lag",
    "cbft_latency_get",
    "elastic_latency_get",
)

SMOOTH_SUBPLOTS = (
    "latency_query",
    "latency_get",
    "latency_set",
    "cbft_latency_get",
    "elastic_latency_get"
)

NON_ZERO_VALUES = (
    "rebalance_progress",
    "bucket_compaction_progress",

    "ops",
    "cmd_get",
    "cmd_set",
    "delete_hits",
    "cas_hits",

    "couch_views_ops",
    "couch_views_data_size",
    "couch_views_actual_disk_size",
    "couch_views_fragmentation",
    "couch_docs_fragmentation",

    "hibernated_waked",

    "ep_dcp_2i_items_sent",
    "ep_dcp_2i_items_remaining",

    "ep_tmp_oom_errors",
    "disk_write_queue",
    "ep_diskqueue_drain",
    "ep_cache_miss_rate",
    "ep_num_value_ejects",
    "ep_bg_fetched",
    "ep_ops_create",
    "ep_ops_update",
    "avg_bg_wait_time",
    "avg_disk_commit_time",
    "avg_disk_update_time",

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

    "query_errors",
    "query_warnings",
    "query_requests_250ms",
    "query_requests_500ms",
    "query_requests_1000ms",
    "query_requests_5000ms",
    "query_invalid_requests",

    "swap_used",

    "data_rbps",
    "data_wbps",
    "data_avgqusz",
    "data_util",
    "index_rbps",
    "index_wbps",
    "index_avgqusz",
    "index_util",

    "TIME_WAIT",
)

PALETTE = (
    "#51A351",
    "#f89406",
    "#7D1935",
    "#4A96AD",
    "#DE1B1B",
    "#E9E581",
    "#A2AB58",
    "#FFE658",
    "#118C4E",
    "#193D4F",
)
