LABELS = {
    "rebalance_progress": "Rebalance progress, %",
    "ops": "Ops per second",
    "cmd_get": "GET ops per second",
    "cmd_set": "SET ops per second",
    "delete_hits": "DELETE ops per second",
    "cas_hits": "CAS ops per second",
    "curr_connections": "Connections",
    "hibernated_waked": "Streaming requests wakeups per second",
    "curr_items": "Active items",
    "vb_replica_curr_items": "Replica items",
    "vb_pending_curr_items": "Pending items",
    "mem_used": "Memory used, bytes",
    "ep_meta_data_memory": "Metadata in RAM, bytes",
    "vb_active_resident_items_ratio": "Active docs resident, %",
    "vb_replica_resident_items_ratio": "Replica docs resident, %",
    "ep_num_value_ejects": "Ejections per second",
    "ep_dcp_2i_items_sent": "DCP drain rate (2i), items/second",
    "ep_dcp_2i_items_remaining": "DCP backlog (2i), items",
    "ep_dcp_replica_items_remaining": "DCP backlog (replica), items",
    "ep_dcp_replica_items_sent": "DCP drain rate (replica), items/second",
    "ep_dcp_replica_total_bytes": "DCP drain rate (replica), bytes/second",
    "ep_dcp_other_items_remaining": "DCP backlog (other), items",
    "ep_dcp_other_items_sent": "DCP drain rate (other), items/second",
    "ep_dcp_other_total_bytes": "DCP drain rate (other), bytes/second",
    "disk_write_queue": "Disk write queue, items",
    "ep_cache_miss_rate": "Cache miss ratio, %",
    "ep_bg_fetched": "Disk reads per second",
    "ep_ops_create": "Disk creates per second",
    "vb_active_ops_create": "Active Create Rate, items/sec",
    "vb_replica_ops_create": "Replica Item Create Rate, items/sec",
    "vb_pending_ops_create": "Pending Create Rate, items/sec",
    "ep_ops_update": "Disk updates per second",
    "vb_active_ops_update": "Active Update Rate, items/sec",
    "vb_replica_ops_update": "Replica Item Update Rate, items/sec",
    "vb_pending_ops_update": "Pending Update Rate, items/sec",
    "ep_diskqueue_drain": "Drain rate, items/second",
    "ep_diskqueue_fill": "Fill rate, items/second",
    "ep_queue_size": "Number of items in the queue, items",
    "avg_bg_wait_time": "BgFetcher wait time, us",
    "avg_disk_commit_time": "Disk commit time, s",
    "avg_disk_update_time": "Disk update time, us",
    "vb_avg_total_queue_age": "Average age of all items in the disk write queue, second",
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
    "bandwidth_usage": "Rate of replication, bytes/second",
    "rate_doc_opt_repd": "Number of optimistically replicated mutations per second",
    "rate_doc_checks": "Number of doc checks per second",
    "wtavg_meta_latency": "Latency of sending getMeta and waiting for conflict solution, ms",
    "wtavg_docs_latency": "Latency of sending replicated mutations to remote cluster, ms",
    "xdc_ops": "Total XDCR operations per second",
    "ep_num_ops_get_meta": "Metadata reads per second",
    "ep_num_ops_set_meta": "Metadata sets per second",
    "ep_num_ops_del_meta": "Metadata deletes per second",
    "couch_views_ops": "View reads per second",
    "couch_views_data_size": "Views data size, bytes",
    "couch_views_actual_disk_size": "Views total disk size, bytes",
    "couch_views_fragmentation": "Views fragmentation, %",
    "cpu_utilization_rate": "CPU utilization across all cores in cluster, %",
    "cpu_utilization": "CPU utilization, %",
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
    "java_rss": "Java resident set size, bytes",
    "java_cpu": "Java CPU utilization, %",
    "cbc-pillowfight_rss": "cbc-pillowfight resident set size, bytes",
    "cbc-pillowfight_cpu": "cbc-pillowfight CPU utilization, %",
    "xdcr_lag": "Total XDCR lag (from memory to memory), ms",
    "xdcr_persistence_time": "Observe latency, ms",
    "xdcr_diff": "Replication lag, ms",
    "latency_set": "SET ops latency, ms",
    "latency_get": "GET ops latency, ms",
    "latency_query": "Query latency, ms",
    "latency_observe": "OBSERVE latency, ms",
    "latency_persist_to": "persistTo=1 latency, ms",
    "latency_replicate_to": "replicateTo=1 latency, ms",
    "data_rps": "Disk reads/second (after merges)",
    "data_wps": "Disk writes/second (after merges)",
    "data_rbps": "Bytes/second read from the disk",
    "data_wbps": "Bytes/second written to the disk",
    "data_avgqusz": "The average queue length",
    "data_util": "Disk bandwidth utilization, %",
    "data_avg_page_cache_rr": "Average page cache resident ratio, %",
    'page_cache_hit_ratio': 'Page cache hit ratio, %',
    'page_cache_total_hits': 'Page cache total hits per second',
    "BlockCacheQuota": "Number of bytes",
    "WriteCacheQuota": "Number of bytes",
    "BlockCacheMemUsed": "Number of bytes",
    "BlockCacheHits": "Number of hits",
    "BlockCacheMisses": "Number of misses",
    "BloomFilterMemUsed": "Number of bytes",
    "BytesIncoming": "Number of bytes",
    "BytesOutgoing": "Number of bytes",
    "BytesPerRead": "Number of bytes",
    "IndexBlocksSize": "Number of bytes",
    "MemoryQuota": "Number of bytes",
    "NCommitBatches": "Number of batches",
    "NDeletes": "Number of deletes",
    "NGets": "Number of gets",
    "NReadBytes": "Number of bytes",
    "NReadBytesCompact": "Number of bytes",
    "NReadBytesGet": "Number of bytes",
    "NReadIOs": "Number of IO",
    "NReadIOsGet": "Number of IO",
    "NSets": "Number of sets",
    "NSyncs": "Number of syncs",
    "NTablesCreated": "Number of tables",
    "NTablesDeleted": "Number of tables",
    "NTableFiles": "Number of table files",
    "TableMetaMemUsed": "Memory used by table metadata",
    "ActiveBloomFilterMemUsed": "Active memory used by bloomfilter",
    "TotalBloomFilterMemUsed": "Total memory used by bloomfilter",
    "NFileCountCompacts": "Number of file count compactions",
    "NWriteBytes": "Number of bytes",
    "NWriteBytesCompact": "Number of bytes",
    "NWriteIOs": "Number of IO",
    "ReadAmp": "Amplification",
    "ReadAmpGet": "Amplification",
    "ReadIOAmp": "Amplification",
    "TotalMemUsed": "Number of bytes",
    "BufferMemUsed": "Number of bytes",
    "WALMemUsed": "Number of bytes",
    "WriteAmp": "Amplification",
    "WriteCacheMemUsed": "Number of bytes",
    "NCompacts": "Number of compactions",
    "TxnSizeEstimate": "Number of bytes",
    "NFlushes": "Number of write cache flushes performed",
    "NGetsPerSec": "Number of gets per second",
    "NSetsPerSec": "Number of sets per second",
    "NDeletesPerSec": "Number of deletes per second",
    "NCommitBatchesPerSec": "Number of commit batches per second",
    "NFlushesPerSec": "Number of flushes per second",
    "NCompactsPerSec": "Number of compacts per second",
    "NSyncsPerSec": "Number of syncs per second",
    "NReadBytesPerSec": "Number of bytes per second",
    "NReadBytesGetPerSec": "Number of bytes per second",
    "NReadBytesCompactPerSec": "Number of bytes per second",
    "BytesOutgoingPerSec": "Number of bytes per second",
    "NReadIOsPerSec": "Number of IOs per second",
    "NReadIOsGetPerSec": "Number of IOs per second",
    "BytesIncomingPerSec": "Number of bytes per second",
    "NWriteBytesPerSec": "Number of bytes per second",
    "NWriteIOsPerSec": "Number of bytes per second",
    "NWriteBytesCompactPerSec": "Number of bytes per second",
    "RecentWriteAmp": "Amplification",
    "RecentReadAmp": "Amplification",
    "RecentReadAmpGet": "Amplification",
    "RecentReadIOAmp": "Amplification",
    "RecentBytesPerRead": "Number of bytes",
    "NGetStatsPerSec": "Number of get stats per second",
    "NGetStatsComputedPerSec": "Number of get stats computed per second",

    "index_rbps": "Bytes read/second",
    "index_wbps": "Bytes written/second",
    "index_avgqusz": "The average queue length",
    "index_util": "Disk bandwidth utilization, %",
    "analytics0_rbps": "Bytes/second read from the disk",
    "analytics0_wbps": "Bytes/second written to the disk",
    "analytics0_util": "Disk bandwidth utilization, %",
    "analytics1_rbps": "Bytes/second read from the disk",
    "analytics1_wbps": "Bytes/second written to the disk",
    "analytics1_util": "Disk bandwidth utilization, %",
    "analytics2_rbps": "Bytes/second read from the disk",
    "analytics2_wbps": "Bytes/second written to the disk",
    "analytics2_util": "Disk bandwidth utilization, %",
    "analytics3_rbps": "Bytes/second read from the disk",
    "analytics3_wbps": "Bytes/second written to the disk",
    "analytics3_util": "Disk bandwidth utilization, %",
    "analytics4_rbps": "Bytes/second read from the disk",
    "analytics4_wbps": "Bytes/second written to the disk",
    "analytics4_util": "Disk bandwidth utilization, %",
    "bucket_compaction_progress": "Compaction progress, %",
    "in_bytes_per_sec": "Incoming bytes/second",
    "out_bytes_per_sec": "Outgoing bytes/second",
    "in_packets_per_sec": "Incoming packets/second",
    "out_packets_per_sec": "Outgoing packets/second",
    "ESTABLISHED": "Connections in ESTABLISHED state",
    "TIME_WAIT": "Connections in TIME_WAIT state",
    "index_num_rows_returned": "Number of rows returned by 2i",
    "index_scan_bytes_read": "Number of bytes per second read by a scan",
    "index_num_requests": "Number of requests served by the indexer per second",
    "index_num_docs_indexed": "Number of documents indexed by the indexer per second",
    "index_num_docs_pending": "Number of pending documents to be indexed",
    "index_num_docs_queued": "Number of queued documents to be indexed",
    "index_fragmentation": "Fragmentation of the index, %",
    "index_data_size": "Actual data size consumed by the index, bytes",
    "index_disk_size": "Total disk file size consumed by the index, bytes",
    "index_total_scan_duration": "Total time spent by 2i on scans",
    "index_items_count": "Current total indexed document count",
    "num_connections": "Number of connections to index node",
    "memory_used": "Memory used, index node, bytes",
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
    "Nth-latency": "latency, ns",
    "flush_queue_size": "Flush queue size, items",
    "avg_scan_wait_latency": "Average scan wait latency, ns",
    "disk_store_duration": "Indexer disk store duration, ms",
    "timings_storage_commit": "Average timings storage commit, ns",
    "timings_storage_del": "Average timings storage del, ns",
    "timings_storage_get": "Average timings storage get, ns",
    "timings_storage_set": "Average timings storage set, ns",
    "timings_storage_snapshot_create": "Average timings storage snapshot create, ns",
    "timings_dcp_getseqs": "Average timings dcp get seq, ns",
    "MainStore_memory_size": "Memory used by plasma",
    "MainStore_num_cached_pages": "Number of pages cached pages by plasma",
    "MainStore_num_pages": "Total number of pages by plasma",
    "MainStore_num_pages_swapout": "Number of pages swapped out by plasma",
    "MainStore_num_pages_swapin": "Number of pages swapped in by plasma",
    "MainStore_bytes_incoming": "Incoming bytes to plasma",
    "MainStore_bytes_written": "Number of bytes written by plasma",
    "MainStore_write_amp": "Write amplification of plasma",
    "MainStore_lss_fragmentation": "lss fragmentation by plasma",
    "MainStore_cache_hits": "Number of cache hits for plasma",
    "MainStore_cache_misses": "Number of cache miss for plasma",
    "MainStore_cache_hit_ratio": "Cache hit ratio",
    "MainStore_rcache_hits": "Number of cache hits in scan path for plasma",
    "MainStore_rcache_misses": "Number of cache miss in scan path for plasma",
    "MainStore_rcache_hit_ratio": "Cache hit ratio in scan path",
    "MainStore_resident_ratio": "Indexer resident ratio for plasma, calculated by items",
    "MainStore_allocated": "Memory allocated for plasma",
    "MainStore_freed": "Memory feed by plasma",
    "MainStore_reclaimed": "Memory reclaimed by plasma",
    "MainStore_mvcc_purge_ratio": "MVCC purge ratio",
    "MainStore_memory_quota": "Indexer Memory quota, Bytes",
    "MainStore_reclaim_pending": "Memory reclaim pending by plasma",
    "MainStore_lss_blk_read_bs": "lss_blk_read_bs, Bytes",
    "MainStore_lss_blk_gc_reads_bs": "lss_blk_gc_reads_bs, Bytes",
    "MainStore_lss_blk_rdr_reads_bs": "lss_blk_rdr_reads_bs, Bytes",
    "BackStore_memory_size": "Memory used by plasma",
    "BackStore_num_cached_pages": "Number of pages cached pages by plasma",
    "BackStore_num_pages": "Total number of pages by plasma",
    "BackStore_num_pages_swapout": "Number of pages swapped out by plasma",
    "BackStore_num_pages_swapin": "Number of pages swapped in by plasma",
    "BackStore_bytes_incoming": "Incoming bytes to plasma",
    "BackStore_bytes_written": "Number of bytes written by plasma",
    "BackStore_write_amp": "Write amplification of plasma",
    "BackStore_lss_fragmentation": "lss fragmentation by plasma",
    "BackStore_cache_hits": "Number of cache hits for plasma",
    "BackStore_cache_misses": "Number of cache miss for plasma",
    "BackStore_cache_hit_ratio": "Cache hit ratio",
    "BackStore_rcache_hits": "Number of cache hits in scan path for plasma",
    "BackStore_rcache_misses": "Number of cache miss in scan path for plasma",
    "BackStore_rcache_hit_ratio": "Cache hit ratio in scan path",
    "BackStore_resident_ratio": "Indexer resident ratio for plasma, calculated by items",
    "BackStore_allocated": "Memory allocated for plasma",
    "BackStore_freed": "Memory feed by plasma",
    "BackStore_reclaimed": "Memory reclaimed by plasma",
    "BackStore_lss_blk_read_bs": "lss_blk_read_bs, Bytes",
    "BackStore_lss_blk_gc_reads_bs": "lss_blk_gc_reads_bs, Bytes",
    "BackStore_lss_blk_rdr_reads_bs": "lss_blk_rdr_reads_bs, Bytes",
    "BackStore_reclaim_pending": "Memory reclaim pending by plasma",
    "BackStore_mvcc_purge_ratio": "MVCC purge ratio",
    "mm_allocated": "Memory allocated, Indexer, bytes",
    "mm_resident": "Memory resident, Indexer, Bytes",
    "mm_metadata": "Memory metadata, Indexer, Bytes",
    "query_requests": "Number of N1QL requests processed per second",
    "query_selects": "Number of N1QL selects processed per second",
    "query_avg_req_time": "Average end-to-end time to process a query, seconds",
    "query_avg_svc_time": "Average time to execute a query, seconds",
    "query_avg_response_size": "Average size of the data returned by a query, Bytes",
    "query_avg_result_count": "Average number of results (documents) returned by a query",
    "query_errors": "Number of N1QL errors returned per second",
    "query_warnings": "Number of N1QL errors returned per second",
    "query_requests_250ms": "Number of queries that take longer than 250ms per second",
    "query_requests_500ms": "Number of queries that take longer than 500ms per second",
    "query_requests_1000ms": "Number of queries that take longer than 1000ms per second",
    "query_requests_5000ms": "Number of queries that take longer than 5000ms per second",
    "query_invalid_requests": "Number of requests for unsupported endpoints per second",
    "cbft_num_bytes_used_disk": "FTS index size on disk in GB",
    "cbft_doc_count": "FTS indexing rate",
    "cbft_num_bytes_used_ram": "FTS ram used by cbft process",
    "cbft_pct_cpu_gc": "FTS garbage collection CPU usage",
    "cbft_query_slow": "FTS slow query",
    "cbft_query_timeout": "FTS timeout query",
    "cbft_query_error": "FTS error query",
    "cbft_batch_merge_count": "FTS batch merge_count",
    "cbft_total_gc": "FTS garbage collector count",
    "cbft_num_bytes_live_data": "FTS live data size",
    "cbft_total_term_searchers": "FTS total term search",
    "cbft_query_total": "FTS total queries",
    "cbft_total_bytes_query_results": "FTS total query bytes",
    "cbft_writer_execute_batch_count": "FTS writer batch count",
    "cbft_latency_get": "FTS latency in ms",
    "cbft_avg_queries_latency": "FTS average queries latency (server)",
    "cbft_query_throughput": "FTS average queries per second",
    "elastic_latency_get": "ElasticSearch latency in ms",
    "cbft_total_bytes_indexed": "FTS total index size",
    "cbft_num_recs_to_persist": "FTS number of records in queue",
    "cbft_num_root_memorysegments": "FTS number of memory segments at root",
    "cbft_num_root_filesegments": "FTS number of disk segments at root",
    "elastic_cache_hit": "Elasticsearch query cache hit",
    "elastic_cache_size": "Elasticsearch query cache size",
    "elastic_filter_cache_size": "Elasticsearch filter cache size",
    "elastic_active_search": "Elasticsearch active search",
    "elastic_query_total": "Elasticsearch total query",
    "jts_throughput": "JTS Throughput, queries/second",
    "jts_latency": "JTS Latency, ms",
    "indexer_pread": "indexer pread system calls/second",
    "indexer_pwrite": "indexer pwrite system calls/second",
    "memcached_pread": "memcached pread system calls/second",
    "memcached_pwrite": "memcached pwrite system calls/second",
    'MemFree': 'The amount of physical memorynot used by the system, bytes',
    'Dirty': 'Memory waiting to be written back to disk, bytes',
    'Buffers': 'Memory in buffer cache, bytes',
    'Cached': 'Memory in the pagecache, bytes',
    'SUnreclaim': 'Memory cannot be reclaimed, bytes',
    'data_bytes_read': 'Total bytes read from the disk',
    'data_bytes_written': 'Total bytes written to the disk',
    "DCP_MUTATION": "DCP mutations processed by function",
    "DOC_TIMER_EVENTS": "DOC timer events processed by function",
    "CRON_TIMER_EVENTS": "CRON timer events processed by function",
    "eventing-produc_rss": "eventing-producer resident set size, bytes",
    "eventing-produc_cpu": "eventing-producer CPU utilization, %",
    "ep_tmp_oom_errors": "Number of back-offs sent per second due to OOM",
    "eventing_consumer_cpu": "Eventing consumer CPU utilization, %",
    "eventing_consumer_rss": "Eventing consumer rss used, Bytes",
    "on_update_success": "OnUpdate() Successful events",
    "DcpEventsRemaining": "DCP events remaining",
    "heap_used": "JVM heap used, bytes",
    "gc_count": "GC count",
    "gc_time": "GC time, ms",
    "io_reads": "IO reads, bytes",
    "io_writes": "IO writes, bytes",
    "system_load_average": "Average load",
    "disk_used": "Total disk used in bytes",
    "thread_count": "Number of threads in use",
    "allocstall": "direct reclaim calls",
    "syncgateway__global__resource_utilization__process_cpu_percent_utilization": "process_cpu_percent_utilization",
    "syncgateway__global__resource_utilization__go_memstats_heapinuse": "go_memstats_heapinuse",
    "syncgateway__per_db__db__database__doc_writes_bytes_blip": "doc_writes_bytes_blip",
    "syncgateway__per_db__db__database__doc_reads_bytes_blip": "doc_reads_bytes_blip",
    "syncgateway__per_db__db__delta_sync__delta_cache_hit": "delta_cache_hit",
    "syncgateway__per_db__db__delta_sync__delta_cache_miss": "delta_cache_miss",
    "syncgateway__per_db__db__cache__rev_cache_hits": "rev_cache_hits",
    "syncgateway__per_db__db__cache__rev_cache_misses": "rev_cache_misses",
    "syncgateway__global__resource_utilization__system_memory_total": "system memory total",
    "syncgateway__global__resource_utilization__admin_net_bytes_sent": "admin_net_bytes_sent",
    "syncgateway__global__resource_utilization__admin_net_bytes_recv": "admin_net_bytes_recv",
    "syncgateway__global__resource_utilization__go_memstats_sys": "go_memstats_sys",
    "syncgateway__global__resource_utilization__go_memstats_heapalloc": "go_memstats_heapalloc",
    "syncgateway__global__resource_utilization__go_memstats_heapidle": "go_memstats_heapidle",
    "syncgateway__global__resource_utilization__go_memstats_heapreleased": "go_memstats_heapreleased",
    "syncgateway__global__resource_utilization__go_memstats_pausetotalns": "go_memstats_pausetotalns",
    "syncgateway__global__resource_utilization__go_memstats_stackinuse": "go_memstats_stackinuse",
    "syncgateway__global__resource_utilization__goroutines_high_watermark": "goroutines_high_watermark",
    "syncgateway__global__resource_utilization__num_goroutines": "num_goroutines",
    "syncgateway__global__resource_utilization__process_memory_resident": "process_memory_resident",
    "syncgateway__global__resource_utilization__pub_net_bytes_recv": "pub_net_bytes_recv",
    "syncgateway__global__resource_utilization__pub_net_bytes_sent": "pub_net_bytes_sent",
    "syncgateway__global__resource_utilization__go_memstats_stacksys": "go_memstats_stacksys",
    "syncgateway__global__resource_utilization__error_count": "error_count",
    "syncgateway__global__resource_utilization__warn_count": "warn_count",
    "syncgateway__per_db__db__cache__rev_cache_bypass": "rev_cache_bypass",
    "syncgateway__per_db__db__cache__chan_cache_hits": "chan_cache_hits",
    "syncgateway__per_db__db__cache__chan_cache_misses": "chan_cache_misses",
    "syncgateway__per_db__db__cache__chan_cache_active_revs": "chan_cache_active_revs",
    "syncgateway__per_db__db__cache__chan_cache_tombstone_revs": "chan_cache_tombstone_revs",
    "syncgateway__per_db__db__cache__chan_cache_removal_revs": "chan_cache_removal_revs",
    "syncgateway__per_db__db__cache__chan_cache_num_channels": "chan_cache_num_channels",
    "syncgateway__per_db__db__cache__chan_cache_max_entries": "chan_cache_max_entries",
    "syncgateway__per_db__db__cache__chan_cache_pending_queries": "chan_cache_pending_queries",
    "syncgateway__per_db__db__cache__chan_cache_channels_added": "chan_cache_channels_added",
    "syncgateway__per_db__db__cache__chan_cache_channels_evicted_inactive": "chan_cache_channels_evicted_inactive",
    "syncgateway__per_db__db__cache__chan_cache_channels_evicted_nru": "chan_cache_channels_evicted_nru",
    "syncgateway__per_db__db__cache__chan_cache_compact_count": "chan_cache_compact_count",
    "syncgateway__per_db__db__cache__chan_cache_compact_time": "chan_cache_compact_time",
    "syncgateway__per_db__db__cache__num_active_channels": "num_active_channels",
    "syncgateway__per_db__db__cache__num_skipped_seqs": "num_skipped_seqs",
    "syncgateway__per_db__db__cbl_replication_pull__attachment_pull_bytes": "attachment_pull_bytes",
    "syncgateway__per_db__db__cbl_replication_pull__attachment_pull_count": "attachment_pull_count",
    "syncgateway__per_db__db__cbl_replication_pull__request_changes_count": "request_changes_count",
    "syncgateway__per_db__db__cbl_replication_pull__request_changes_time": "request_changes_time",
    "syncgateway__per_db__db__cbl_replication_pull__rev_processing_time": "rev_processing_time",
    "syncgateway__per_db__db__cbl_replication_pull__rev_send_count": "rev_send_count",
    "syncgateway__per_db__db__cbl_replication_pull__rev_send_latency": "rev_send_latency",
    "syncgateway__per_db__db__cbl_replication_push__attachment_push_bytes": "attachment_push_bytes",
    "syncgateway__per_db__db__cbl_replication_push__attachment_push_count": "attachment_push_count",
    "syncgateway__per_db__db__cbl_replication_push__doc_push_count": "doc_push_count",
    "syncgateway__per_db__db__cbl_replication_push__propose_change_count": "propose_change_count",
    "syncgateway__per_db__db__cbl_replication_push__propose_change_time": "propose_change_time",
    "syncgateway__per_db__db__cbl_replication_push__sync_function_count": "sync_function_count",
    "syncgateway__per_db__db__cbl_replication_push__sync_function_time": "sync_function_time",
    "syncgateway__per_db__db__cbl_replication_push__write_processing_time": "write_processing_time",
    "syncgateway__per_db__db__database__doc_writes_bytes": "doc_writes_bytes",
    "syncgateway__per_db__db__database__num_doc_reads_blip": "num_doc_reads_blip",
    "syncgateway__per_db__db__database__num_doc_reads_rest": "num_doc_reads_rest",
    "syncgateway__per_db__db__database__num_doc_writes": "num_doc_writes",
    "syncgateway__per_db__db__cache__abandoned_seqs": "abandoned_seqs",
    "syncgateway__per_db__db__cache__high_seq_cached": "high_seq_cached",
    "syncgateway__per_db__db__cache__high_seq_stable": "high_seq_stable",
    "syncgateway__per_db__db__cache__skipped_seq_len": "skipped_seq_len",
    "syncgateway__per_db__db__cache__pending_seq_len": "pending_seq_len",
    "syncgateway__per_db__db__database__sequence_get_count": "sequence_get_count",
    "syncgateway__per_db__db__database__sequence_incr_count": "sequence_incr_count",
    "syncgateway__per_db__db__database__sequence_reserved_count": "sequence_reserved_count",
    "syncgateway__per_db__db__database__sequence_assigned_count": "sequence_assigned_count",
    "syncgateway__per_db__db__database__sequence_released_count": "sequence_released_count",
    "syncgateway__per_db__db__database__crc32c_match_count": "crc32c_match_count",
    "syncgateway__per_db__db__database__num_replications_active": "num_replications_active",
    "syncgateway__per_db__db__database__num_replications_total": "num_replications_total",
    "syncgateway__per_db__db__delta_sync__delta_pull_replication_count": "delta_pull_replication_count",
    "syncgateway__per_db__db__delta_sync__delta_push_doc_count": "delta_push_doc_count",
    "syncgateway__per_db__db__database__num_tombstones_compacted": "num_tombstones_compacted",
    "syncgateway__per_db__db__database__doc_writes_xattr_bytes": "doc_writes_xattr_bytes",
    "syncgateway__per_db__db__database__warn_xattr_size_count": "warn_xattr_size_count",
    "syncgateway__per_db__db__database__warn_channels_per_doc_count": "warn_channels_per_doc_count",
    "syncgateway__per_db__db__database__warn_grants_per_doc_count": "warn_grants_per_doc_count",
    "syncgateway__per_db__db__database__dcp_received_count": "dcp_received_count",
    "syncgateway__per_db__db__database__high_seq_feed": "high_seq_feed",
    "syncgateway__per_db__db__database__dcp_received_time": "dcp_received_time",
    "syncgateway__per_db__db__database__dcp_caching_count": "dcp_caching_count",
    "syncgateway__per_db__db__database__dcp_caching_time": "dcp_caching_time",
    "syncgateway__per_db__db__delta_sync__deltas_requested": "deltas_requested",
    "syncgateway__per_db__db__delta_sync__deltas_sent": "deltas_sent",
    "syncgateway__per_db__db__shared_bucket_import__import_count": "import_count",
    "syncgateway__per_db__db__shared_bucket_import__import_cancel_cas": "import_cancel_cas",
    "syncgateway__per_db__db__shared_bucket_import__import_error_count": "error_count",
    "syncgateway__per_db__db__shared_bucket_import__import_processing_time": "import_processing_time",
    "syncgateway__per_db__db__cbl_replication_push__conflict_write_count": "conflict_write_count",
    "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_active_one_shot": "num_pull_repl_active_one_shot",
    "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_active_continuous": "num_pull_repl_active_continuous",
    "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_total_one_shot": "num_pull_repl_total_one_shot",
    "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_total_continuous": "num_pull_repl_total_continuous",
    "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_since_zero": "num_pull_repl_since_zero",
    "syncgateway__per_db__db__cbl_replication_pull__num_pull_repl_caught_up": "num_pull_repl_caught_up",
    "syncgateway__per_db__db__cbl_replication_pull__max_pending": "pull__max_pending",
    "syncgateway__per_db__db__security__num_docs_rejected": "num_docs_rejected",
    "syncgateway__per_db__db__security__num_access_errors": "num_access_errors",
    "syncgateway__per_db__db__security__auth_success_count": "auth_success_count",
    "syncgateway__per_db__db__security__auth_failed_count": "auth_failed_count",
    "syncgateway__per_db__db__security__total_auth_time": "total_auth_time",
    "syncGateway_import__import_count": "import_count",
    "sgimport_latency": "sgimport_latency",
    "syncgateway__per_db__db__gsi_views__access_count": "gsi_views__access_count",
    "syncgateway__per_db__db__gsi_views__roleAccess_count": "gsi_views__roleAccess_count",
    "syncgateway__per_db__db__gsi_views__channels_count": "gsi_views__channels_count",
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
    "vb_avg_total_queue_age",
    "query_avg_req_time",
    "query_avg_svc_time",
    "cbft_latency_get",
    "elastic_latency_get",
    "Nth-latency",
    "sgimport_latency",
)

ZOOM_HISTOGRAMS = (
    "latency_get",
    "latency_set",
    "latency_query",
    "avg_bg_wait_time",
    "cbft_latency_get",
    "elastic_latency_get",
    "Nth-latency",
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
    "ep_dcp_replica_items_remaining",
    "ep_dcp_replica_items_sent",
    "ep_dcp_replica_total_bytes",
    "ep_dcp_other_items_remaining",
    "ep_dcp_other_items_sent",
    "ep_dcp_other_total_bytes",

    "ep_tmp_oom_errors",
    "disk_write_queue",
    "ep_diskqueue_drain",
    "ep_diskqueue_fill",
    "ep_queue_size",
    "ep_cache_miss_rate",
    "ep_num_value_ejects",
    "ep_bg_fetched",
    "ep_ops_create",
    "vb_active_ops_create",
    "vb_replica_ops_create",
    "vb_pending_ops_create",
    "ep_ops_update",
    "vb_active_ops_update",
    "vb_replica_ops_update",
    "vb_pending_ops_update",
    "avg_bg_wait_time",
    "avg_disk_commit_time",
    "avg_disk_update_time",
    "vb_replica_curr_items",
    "vb_pending_curr_items",
    "vb_avg_total_queue_age",

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
    "ActiveBloomFilterMemUsed",
    "TotalBloomFilterMemUsed",
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

    "xdc_ops",
    "ep_num_ops_get_meta",
    "ep_num_ops_set_meta",
    "ep_num_ops_del_meta",
    "docs_failed_cr_source",
    "docs_filtered",
    "docs_failed_cr_source",
    "rate_doc_opt_repd",
    "rate_doc_checks",

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

    "index_fragmentation",
    "index_items_count",
    "index_num_docs_indexed",
    "index_num_docs_pending",
    "index_num_docs_queued",
    "index_num_requests",
    "index_num_rows_returned",
    "index_scan_bytes_read",
    "index_data_size",
    "index_disk_size",
    "index_total_scan_duration",

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

    "DCP_MUTATION",
    "DOC_TIMER_EVENTS",
    "CRON_TIMER_EVENTS",

    "swap_used",

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

    "TIME_WAIT",

    "syncGateway_rest__requests_0000ms",
    "syncGateway_rest__requests_0100ms",
    "syncGateway_rest__requests_0200ms",
    "syncGateway_rest__requests_0300ms",
    "syncGateway_rest__requests_0700ms",
    "syncGateway_rest__requests_0800ms",
    "syncGateway_rest__requests_0900ms",
    "syncGateway_rest__requests_1000ms",
    "syncGateway_stats__bulkApi.BulkDocsRollingMean",
    "syncGateway_stats__bulkApi.BulkGetPerDocRollingMean",
    "syncGateway_stats__bulkApi.BulkGetRollingMean",
    "syncGateway_stats__bulkApi_BulkDocsPerDocRollingMean",
    "syncGateway_stats__indexReader.getChanges.Count",
    "syncGateway_stats__indexReader.getChanges.Time",
    "syncGateway_stats__indexReader.getChanges.UseCached",
    "syncGateway_stats__indexReader.getChanges.UseIndexed",
    "syncGateway_stats__indexReader.numReaders.OneShot",
    "syncGateway_stats__indexReader.numReaders.Persistent",
    "syncGateway_stats__indexReader.pollPrincipals.Count",
    "syncGateway_stats__indexReader.pollPrincipals.Time:",
    "syncGateway_stats__indexReader.pollReaders.Count",
    "syncGateway_stats__indexReader.pollReaders.Time",
    "syncGateway_stats__indexReader.seqHasher.GetClockTime",
    "syncGateway_stats__indexReader.seqHasher.GetHash",
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
