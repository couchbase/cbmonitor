from django.http import Http404
from django.shortcuts import render_to_response

from cbmonitor.plotter import Plotter


def base(request):
    snapshot = request.GET.get("snapshot")
    if snapshot is None:
        raise Http404
    plotter = Plotter()
    charts = list(plotter.html(snapshot))
    if charts:
        return render_to_response("reports/base.jade", {"charts": charts})
    else:
        raise Http404
