import json
import time
from collections import defaultdict

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers

from models import Settings, Value, TestResults


def dashboard(request):
    """Main litmus dashboard"""
    return render_to_response('litmus.jade')


def update_or_create(testcase, env, build, metric, value=None, comment=None):
    """Update testresults/settings if exist, otherwise create new ones.

    :return created     True if created new results, otherwise False
    """

    settings = Settings.objects.get_or_create(testcase=testcase,
                                              metric=metric)[0]

    testresults, created = TestResults.objects.get_or_create(build=build,
                                                             testcase=testcase, env=env,
                                                             metric=metric, settings=settings)
    testresults.timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    if value:
        v = Value(value=value)
        testresults.value_set.add(v)
    if comment:
        testresults.comment = comment
    testresults.save()

    return created


@csrf_exempt
@require_POST
def post(request):
    """REST API for posting litmus results.

    build -- build version (e.g., '2.0.0-1723-rel-enterprise')
    testcase -- testcase (e.g: 'lucky6')
    env -- test enviornment (e.g, 'terra')
    metric -- metric name (e.g., 'Rebalance time, sec')
    value -- metric value (e.g., 610)

    It supports multivalued query parameters.

    Sample request:
        curl -d "build=2.0.0-1723-rel-enterprise\
                 &testcase=lucky6&env=terra\
                 &metric=Latency, ms&value=555\
                 &metric=Query throughput&value=1746" \
            -X POST http://localhost:8000/litmus/post/
    """
    try:
        build = request.POST['build'].strip()
        testcase = request.POST['testcase'].strip()
        env = request.POST['env'].strip()
        metrics = request.POST.getlist('metric')
        values = request.POST.getlist('value')
    except KeyError, e:
        return HttpResponse(e, status=400)

    for metric, value in zip(metrics, values):
        created = update_or_create(testcase, env, build, metric, value)
    return HttpResponse(content='Created' if created else 'Updated')


@require_GET
def get(request):
    """REST API for getting litmus results.

    Sample request to get all test results:
        curl http://localhost:8000/litmus/get?all
        curl http://localhost:8000/litmus/get

    Sample request to get specific results:
        curl -G http://localhost:8000/litmus/get \
            -d "testcase=lucky6&metric=Latency,%20ms"

    JSON response:
        [["Testcase", "Env", "Metric", "Timestamp",
         "2.0.0-1723-rel-enterprise", "2.0.0-1724-rel-enterprise"], \
         ["lucky6", "terra", "Query throughput", "2012-10-16 11:10:30",
          "1024", "610"], \
         ["mixed-2suv", "vesta", "Latency, ms", "2012-10-16 11:16:31",
         "777", ""]]
    """
    if not request.GET or 'all' in request.GET:
        objs = TestResults.objects.all()
    else:
        criteria = dict((key, request.GET[key]) for key in request.GET.iterkeys())
        objs = TestResults.objects.filter(**criteria)

    builds = objs.values('build').order_by('build').reverse().distinct()
    agg_stats = defaultdict(dict)
    for obj in objs:
        key = "%s-%s-%s" % (obj.testcase, obj.env, obj.metric)
        agg_stats[key]['testcase'] = obj.testcase
        agg_stats[key]['env'] = obj.env
        agg_stats[key]['metric'] = obj.metric
        agg_stats[key]['timestamp'] = obj.timestamp
        agg_stats[key][obj.build] = " / ".join(map(lambda v: str(v.value),
                                               obj.value_set.all()))

    response = [['Testcase', 'Env', 'Metric', 'Timestamp']
                + [row['build'] for row in builds], ]
    for key, val in agg_stats.iteritems():
        row = [val['testcase'], val['env'], val['metric'], val['timestamp'], ]
        for build in response[0][4:]:
            try:
                row.append(val[build])
            except KeyError:
                row.append('')
        response.append(row)

    return HttpResponse(json.dumps(response), mimetype='application/json')

@csrf_exempt
@require_POST
def post_comment(request):
    """REST API to post comment for litmus results.

    build -- build version (e.g., '2.0.0-1723-rel-enterprise')
    testcase -- testcase (e.g: 'lucky6')
    env -- test enviornment (e.g, 'terra')
    metric -- metric name (e.g., 'Latency, ms')
    comment -- comment string (e.g, 'Regression for RC1')

    Sample request:
        curl -d "testcase=lucky6\
                 &env=terra\
                 &build=2.0.0-1723-rel-enterprise\
                 &metric=Latency, ms\
                 &comment=Regression for RC1" \
            -X POST http://localhost:8000/litmus/post/comment/
    """
    try:
        testcase = request.POST['testcase'].strip()
        env = request.POST['env'].strip()
        build = request.POST['build'].strip()
        metric = request.POST['metric'].strip()
        comment = request.POST['comment'].strip()
    except KeyError, e:
        return HttpResponse(e, status=400)

    update_or_create(testcase, env, build, metric, comment=comment)

    return HttpResponse(content=comment)

@require_GET
def get_comment(request):
    """REST API to get comment for litmus results.

    build -- build version (e.g., '2.0.0-1723-rel-enterprise')
    testcase -- testcase (e.g: 'lucky6')
    env -- test enviornment (e.g, 'terra')
    metric -- metric name (e.g., 'Rebalance time, sec')

    Sample request:
        curl -G http://localhost:8000/litmus/get/comment \
            -d "testcase=lucky6&env=terra&build=2.0.0-1723-rel-enterprise&metric=Latency,%20ms"
    """
    try:
        testcase = request.GET['testcase'].strip()
        env = request.GET['env'].strip()
        build = request.GET['build'].strip()
        metric = request.GET['metric'].strip()
    except KeyError, e:
        return HttpResponse(e, status=400)

    objs = TestResults.objects.filter(testcase=testcase, env=env,
                                      build=build, metric=metric).distinct()

    if not objs:
        return HttpResponse("empty result set", status=404)

    return HttpResponse(content=objs[0].comment)

@require_GET
def get_settings(request):
    """REST API to get settings for litmus results.

    testcase -- testcase (e.g: 'lucky6')
    metric -- metric name (e.g., 'Latency, ms')

    Sample request to get all settings:
        curl http://localhost:8000/litmus/get/settings?all
        curl http://localhost:8000/litmus/get/settings

    Sample request to get a specific setting:
        curl -G http://localhost:8000/litmus/get/settings \
            -d "testcase=lucky6&metric=Latency,%20ms"
    """
    if not request.GET or 'all' in request.GET:
        response = map(lambda d: d["fields"],
                       serializers.serialize("python", Settings.objects.all()))
        return HttpResponse(content=json.dumps(response))

    try:
        testcase = request.GET['testcase'].strip()
        metric = request.GET['metric'].strip()
    except KeyError, e:
        return HttpResponse(e, status=400)

    try:
        obj = Settings.objects.get(testcase=testcase, metric=metric)
    except ObjectDoesNotExist:
        return HttpResponse("empty result set", status=404)

    response = map(lambda d: d["fields"],
                   serializers.serialize("python", [ obj, ]))

    return HttpResponse(content=json.dumps(response))
