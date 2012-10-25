import json
import time
from collections import defaultdict

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

from models import TestResults


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

    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    for metric, value in zip(metrics, values):
        TestResults.objects.create(build=build, metric=metric, value=value,
                                   timestamp=timestamp)
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
    metrics = TestResults.objects.values('metric').distinct()
    all_stats = TestResults.objects.values().distinct()
    agg_stats = defaultdict(dict)
    for stat in all_stats:
        agg_stats[stat['build']][stat['metric']] = stat['value']
        agg_stats[stat['build']]['Timestamp'] = stat['timestamp']

    response = [['Build', 'Timestamp'] + [row['metric'] for row in metrics], ]
    for build, metrics in agg_stats.iteritems():
        row = [build, ]
        for metric in response[0][1:]:
            try:
                row.append(metrics[metric])
            except KeyError:
                row.append('')
        response.append(row)

    return HttpResponse(json.dumps(response), mimetype='application/json')
