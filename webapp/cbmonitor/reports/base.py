from django.core.exceptions import ObjectDoesNotExist

from cbmonitor import models


class BaseReport(object):

    METRICS = {
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
        ]
    }

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def __iter__(self):
        for collector, metrics in self.METRICS.iteritems():
            for metric in metrics:
                try:
                    yield models.Observable.objects.get(
                        cluster=self.snapshot.cluster,
                        type_id="metric",
                        collector=collector,
                        name=metric,
                        server__isnull=True,
                        bucket__isnull=False,
                    )
                except ObjectDoesNotExist:
                    continue
