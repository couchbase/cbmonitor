from django.http import Http404
from django.shortcuts import render_to_response

from cbmonitor.rest_api import html


def tab(request):
    path = request.path.replace("/", "") or "inventory"
    if path in ("inventory", "charts", "snapshots"):
        template = "{0}/{0}".format(path) + ".jade"
        return render_to_response(template, {path: True})
    else:
        raise Http404


def report(request):
    urls = html(request)
    if urls:
        return render_to_response("report.jade", {"urls": urls})
    else:
        raise Http404
