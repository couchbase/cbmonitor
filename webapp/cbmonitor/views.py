from django.http import Http404
from django.shortcuts import render_to_response, redirect

from cbmonitor import models
from cbmonitor.plotter import Plotter
from cbmonitor.reports import Report


def tab(request):
    path = request.path.replace("/", "") or "charts"
    if path in ("inventory", "charts"):
        template = "{0}".format(path) + ".jade"
        return render_to_response(template, {path: True})
    else:
        raise Http404


def get_plotter_and_metrics(params):
    snapshot = params.get("snapshot")
    if snapshot == "all_data":
        snapshot = type("snapshot", (object, ), {"name": "all_data"})()
        cluster = params["cluster"]
    else:
        snapshot = models.Snapshot.objects.get(name=snapshot)
        cluster = snapshot.cluster
    plotter = Plotter(snapshot)
    metrics = Report(cluster, params["report"])
    return plotter, metrics


def render_png(*args, **kwargs):
    plotter, metrics = get_plotter_and_metrics(*args, **kwargs)
    plotter.plot(metrics)
    id_from_url = lambda url: url.split("/")[2].split(".")[0]
    return [(id_from_url(url), title, url) for title, url in plotter.urls]


def pdf_report(request):
    plotter, metrics = get_plotter_and_metrics(request.GET)
    url = plotter.pdf(metrics)
    return redirect(url)


def html_report(request):
    urls = render_png(request.GET)
    if urls:
        return render_to_response("report.jade", {"urls": urls})
    else:
        raise Http404
