from django.http import Http404
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page

from cbmonitor import models
from cbmonitor.plotter import Plotter
from cbmonitor.reports import Report


def index(request):
    return render_to_response("charts.jade", {"charts": True})


def get_plotter_and_metrics(params):
    snapshots = []
    if "all_data" in params.getlist("snapshot"):
        for cluster in params.getlist("cluster"):
            snapshots.append((
                type("snapshot", (object, ), {"name": "all_data"})(),
                cluster
            ))
    else:
        for snapshot in params.getlist("snapshot"):
            snapshot = models.Snapshot.objects.get(name=snapshot)
            snapshots.append((snapshot, snapshot.cluster))
    plotter = Plotter()
    metrics = Report(snapshots, params["report"])
    return plotter, metrics


def render_png(params):
    plotter, metrics = get_plotter_and_metrics(params)
    plotter.plot(metrics)
    id_from_url = lambda url: url.split("/")[2].split(".")[0]
    return [(id_from_url(url), title, url) for title, url in plotter.urls]


@cache_page()
def html_report(request):
    urls = render_png(request.GET)
    if urls:
        return render_to_response("report.jade", {"urls": urls})
    else:
        raise Http404
