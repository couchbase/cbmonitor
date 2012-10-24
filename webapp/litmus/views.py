import json
import time

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from couchbase.client import Couchbase
from couchbase.exception import MemcachedError


def dashboard(request):
    """Main litmus dashboard"""
    return render_to_response('litmus.jade')


@csrf_exempt
@require_POST
def post(request):
    """REST API for posting litmus results.

    build -- build version (e.g., '2.0.0-1723-rel-enterprise')
    metric -- metric name (e.g., 'Rebalance time, sec')
    value -- metric value (e.g., 610)

    It supports multivalued query parameters.

    Sample request:
        curl -d "build=2.0.0-1723-rel-enterprise\
                 &metric=Latency, ms&value=555\
                 &metric=Query throughput&value=1746" \
            -X POST http://localhost:8000/litmus/post/
    """
    try:
        build = request.POST['build']
        metrics = request.POST.getlist('metric')
        values = request.POST.getlist('value')
    except KeyError as e:
        return HttpResponse(e, status=400)

    bucket_handler = get_bucket_handler()
    try:
        r = bucket_handler.get(build)
        build_data = eval(r[-1])
    except MemcachedError:
        build_data = dict()

    build_data['Timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime())
    for metric, value in zip(metrics, values):
        build_data[metric] = value
    bucket_handler.set(build, 0, 0, build_data)
    return HttpResponse(content='Success')


@require_GET
def get(request):
    """REST API for getting litmus results.

    Sample request:
        curl http://localhost:8000/litmus/get/

    JSON response:
        [["Build", "Timestamp", "Query throughput", "Rebalance time, sec"], \
         ["2.0.0-1723-rel-enterprise", "2012-10-16 11:10:30", "1024", "610"], \
         ["2.0.0-1724-rel-enterprise", "2012-10-16 11:16:31", "777", ""]]
    """
    bucket = get_bucket_handler()

    builds = bucket.view('_design/{0}/_view/{1}'.format('litmus', 'dashboard'),
                         stale='false', limit=1000)

    header = set(key for build in builds for key in build['value'].keys()) - \
        set(('Timestamp', ))

    response = [['Build', 'Timestamp'] + list(header), ]

    for build in builds:
        row = [build['key']]
        for column in response[0][1:]:
            try:
                row.append(build['value'][column])
            except KeyError:
                row.append('')
        response.append(row)

    return HttpResponse(json.dumps(response), mimetype='application/json')


def get_bucket_handler():
    """Return instance of Couchbase client"""
    cb = Couchbase(settings.COUCHBASE['HOST'],
                   settings.COUCHBASE['USERNAME'],
                   settings.COUCHBASE['PASSWORD'])

    return cb[settings.COUCHBASE['BUCKET']]
