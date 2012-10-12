import json

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings

from couchbase.client import Couchbase

BUCKET_NAME = settings.CB_BUCKET
CB = Couchbase("%s:%s" % (settings.CB_HOST, settings.CB_PORT),
               BUCKET_NAME, "")
BUCKET = CB[BUCKET_NAME]

def demo_flot(request):
    return render_to_response('demo_flot.html')


def demo_rickshaw(request):
    return render_to_response('demo_rickshaw.html')


def litmus(request):
    return render_to_response('dashboard/litmus.jade')


def cbdata(request):

    view = BUCKET.view("_design/%s/_view/%s"\
                       % (request.GET["ddoc"], request.GET["view"]))
    results = json.dumps(view)

    print "[cbdata] request: %s, results: %s" % (request.GET, results)

    return HttpResponse(results, mimetype="application/json")
