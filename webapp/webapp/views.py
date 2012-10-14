import json

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings

from couchbase.client import Couchbase


def demo_flot(request):
    return render_to_response('demo_flot.html')


def demo_rickshaw(request):
    return render_to_response('demo_rickshaw.html')


def litmus(request):
    return render_to_response('dashboard/litmus.jade')


def cbdata(request):
    cb = Couchbase(settings.COUCHBASE['HOST'],
                   settings.COUCHBASE['USERNAME'],
                   settings.COUCHBASE['PASSWORD'])

    bucket = cb[settings.COUCHBASE['BUCKET']]

    view = bucket.view("_design/{0}/_view/{1}".format(request.GET["ddoc"],
                                                      request.GET["view"]))
    results = json.dumps(view)

    return HttpResponse(results, mimetype="application/json")


def demo_nvd3(request):
    return render_to_response('demo_nvd3.html')


def demo_cubism(request):
    return render_to_response('demo_cubism.html')
