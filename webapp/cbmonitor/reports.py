from django.core.exceptions import ObjectDoesNotExist

from cbmonitor import models


class Report(object):

    def __new__(cls, cluster, report_type):
        if report_type == "BaseReport":
            return BaseReport(cluster)
        elif report_type == "FullReport":
            return FullReport(cluster)
        elif report_type == "BaseXdcrReport":
            return BaseXdcrReport(cluster)
        elif report_type == "BaseViewsReport":
            return BaseViewsReport(cluster)
        else:
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

    def __init__(self, cluster):
        self.cluster = cluster

    def __iter__(self):
        for collector, metrics in self.metrics.iteritems():
            for metric in metrics:
                try:
                    for observable in models.Observable.objects.filter(
                        cluster=self.cluster,
                        type_id="metric",
                        collector=collector,
                        name=metric,
                        server__isnull=True,
                        bucket__isnull=False,
                    ):
                        yield observable
                except ObjectDoesNotExist:
                    continue


class BaseXdcrReport(BaseReport):

    def merge_metrics(self):
        base_metrics = super(BaseXdcrReport, self).metrics
        for collector in set(base_metrics) & set(self.metrics):
            self.metrics[collector] += base_metrics[collector]
        self.metrics = dict(base_metrics, **self.metrics)

    def __init__(self, *args, **kwargs):
        self.metrics = {
            "xdcr_lag": [
                "xdcr_lag",
                "xdcr_persistence_time",
                "xdcr_diff",
            ],
            "ns_server": [
                "xdc_ops",
                "replication_changes_left"
            ]
        }
        self.merge_metrics()
        super(BaseXdcrReport, self).__init__(*args, **kwargs)


class BaseViewsReport(BaseReport):

    def merge_metrics(self):
        base_metrics = super(BaseViewsReport, self).metrics
        for collector in set(base_metrics) & set(self.metrics):
            self.metrics[collector] += base_metrics[collector]
        self.metrics = dict(base_metrics, **self.metrics)

    def __init__(self, *args, **kwargs):
        self.metrics = {
            "query_latency": [
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


class FullReport(BaseReport):

    def __iter__(self):
        return models.Observable.objects.filter(
            cluster=self.cluster, type_id="metric").__iter__()
