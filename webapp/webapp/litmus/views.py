import json

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings

from couchbase.client import Couchbase


def litmus(request):
    return render_to_response('litmus/litmus.jade')


def cbdata(request):
    cb = Couchbase(settings.COUCHBASE['HOST'],
                   settings.COUCHBASE['USERNAME'],
                   settings.COUCHBASE['PASSWORD'])

    bucket = cb[settings.COUCHBASE['BUCKET']]

    view = bucket.view("_design/{0}/_view/{1}".format(request.GET["ddoc"],
                                                      request.GET["view"]))
    results = json.dumps(view)

    return HttpResponse(results, mimetype="application/json")
