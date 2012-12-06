import json

from django.http import HttpResponse
from django.shortcuts import render_to_response

from pdffinder import PDFFinder


def index(request):
    return render_to_response('reports.jade')


def search(request):
    testcase = request.GET.get("testcase", None)
    build = request.GET.get("build", None)
    query = [word for word in (testcase, build) if word]

    if query:
        urls = PDFFinder().search(query)
        return HttpResponse(content=json.dumps(urls))
    else:
        return HttpResponse(content="Bad query", status=400)
