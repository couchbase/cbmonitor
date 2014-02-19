from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from cbmonitor import views

admin.autodiscover()


@csrf_exempt
def restful_dispatcher(request, path):
    handler = {
        "add_cluster": views.add_cluster,
        "add_server": views.add_server,
        "add_bucket": views.add_bucket,
        "add_metric": views.add_metric,
        "add_snapshot": views.add_snapshot,
        "get_clusters": views.get_clusters,
        "get_all_snapshots": views.get_all_snapshots,
        "get_servers": views.get_servers,
        "get_buckets": views.get_buckets,
        "get_snapshots": views.get_snapshots,
        "get_metrics": views.get_metrics,
        "delete_cluster": views.delete_cluster,
        "get_insight_defaults": views.get_insight_defaults,
        "get_insight_options": views.get_insight_options,
        "get_insight_data": views.get_insight_data,
    }.get(path)
    if handler:
        return handler(request)
    else:
        return HttpResponse(content="Wrong path: {}".format(path), status=404)

urlpatterns = patterns(
    "",
    url(r"^$", "cbmonitor.views.index"),
    url(r"^favicon\.ico$", RedirectView.as_view(url="/static/favicon.ico")),
    url(r"^insight/", "cbmonitor.views.insight"),
    url(r"^reports/get_corr_matrix/", "cbmonitor.views.get_corr_matrix"),
    url(r"^reports/corr/", "cbmonitor.views.corr_matrix"),
    url(r"^reports/html/", "cbmonitor.views.html_report"),
    url(r"^reports/compare/", "cbmonitor.views.compare_snapshots"),
    url(r"^cbmonitor/(?P<path>[a-z_]+)/$", restful_dispatcher),
    url(r"^seriesly/", "cbmonitor.views.seriesly_proxy"),
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    url(r"^admin/", include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns(
        "",
        (r"^media/(?P<path>.*)$", "django.views.static.serve",
         {"document_root": settings.MEDIA_ROOT})
    )
