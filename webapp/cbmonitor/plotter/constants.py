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
    "ep_upr_replica_items_remaining": "UPR replication backlog",
    "ep_dcp_replica_items_remaining": "UPR replication backlog",
    "disk_write_queue": "Disk write queue, items",
    "ep_cache_miss_rate": "Cache miss ratio, %",
    "ep_bg_fetched": "Disk reads per sec",
    "ep_diskqueue_drain": "Drain rate, items/sec",
    "avg_bg_wait_time": "BgFetcher wait time, us",
    "avg_disk_commit_time": "Disk commit time, s",
    "avg_disk_update_time": "Disk update time, us",
    "couch_docs_data_size": "Docs data size, bytes",
    "couch_docs_actual_disk_size": "Docs total disk size, bytes",
    "couch_docs_fragmentation": "Docs fragmentation, %",
    "couch_total_disk_size": "Total disk size, bytes",
    "replication_changes_left": "Outbound XDCR mutations, items",
    "replication_size_rep_queue": "XDC replication queue, bytes",
    "replication_rate_replication": "Mutation replication rate per sec",
    "replication_bandwidth_usage": "Data replication rate, bytes/sec",
    "replication_work_time": "Secs in replicating",
    "replication_commit_time": "Secs in checkpointin",
    "replication_active_vbreps": "Active vbucket replications",
    "replication_waiting_vbreps": "Waiting vbucket replications",
    "replication_num_checkpoints": "Checkpoints issued",
    "replication_num_failedckpts": "Checkpoints failed",
    "replication_meta_latency_wt": "Weighted meta ops latency, ms",
    "replication_docs_latency_wt": "Weighted doc ops latency, ms",
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
    "memcached_rss": "memcached resident set size, bytes",
    "memcached_cpu": "memcached CPU utilization, %",
    "sync_gateway_rss": "Sync Gateway resident set size, bytes",
    "sync_gateway_cpu": "Sync Gateway CPU utilization, %",
    "xdcr_lag": "Total XDCR lag (from memory to memory), ms",
    "xdcr_persistence_time": "Observe latency, ms",
    "xdcr_diff": "Replication lag, ms",
    "latency_set": "SET ops latency, ms",
    "latency_get": "GET ops latency, ms",
    "latency_query": "Query latency, ms",
    "latency_observe": "OBSERVE latency, ms",
    "Sys": "Bytes obtained from system",
    "Alloc": "Bytes allocated and still in use",
    "HeapAlloc": "Bytes allocated and still in use",
    "HeapObjects": "Total number of allocated objects",
    "PauseTotalNs": "Total GC pause time, ns",
    "PauseNs": "GC pause time, ns",
    "NumGC": "GC events",
    "PausesPct": "Percentage of total time spent in GC, %",
    "gateway_push": "Single push request to SGW, ms",
    "gateway_pull": "Single pull request to SGW, ms",
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
}

HISTOGRAMS = (
    "latency_get", "latency_set", "latency_query", "latency_observe",
    "xdcr_lag", "xdcr_persistence_time", "xdcr_diff",
    "replication_meta_latency_wt", "replication_docs_latency_wt",
    "avg_bg_wait_time", "avg_disk_commit_time", "avg_disk_update_time",
)

ZOOM_HISTOGRAMS = (
    "latency_get", "latency_set", "latency_query", "avg_bg_wait_time",
)

KDE = (
    "latency_query", "latency_get", "latency_set", "xdcr_lag",
)

SMOOTH_SUBPLOTS = (
    "latency_query", "latency_get", "latency_set",
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

    "ep_tmp_oom_errors",
    "disk_write_queue",
    "ep_diskqueue_drain",
    "ep_cache_miss_rate",
    "ep_num_value_ejects",
    "ep_bg_fetched",
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

    "bucket_compaction_progress",

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
