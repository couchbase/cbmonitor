import json
import logging

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist as DoesNotExist
from django.db.utils import IntegrityError
from cbagent.collectors import Collector

from cbmonitor import models
from cbmonitor import forms
from cbmonitor.plotter import Plotter

logger = logging.getLogger(__name__)


@csrf_exempt
def dispatcher(request, path):
    handler = {
        "add_cluster": add_cluster,
        "add_server": add_server,
        "add_bucket": add_bucket,
        "delete_cluster": delete_cluster,
        "delete_server": delete_server,
        "delete_bucket": delete_bucket,
        "get_tree_data": get_tree_data,
        "get_clusters": get_clusters,
        "get_servers": get_servers,
        "get_buckets": get_buckets,
        "get_metrics_and_events": get_metrics_and_events,
        "add_metric_or_event": add_metric_or_event,
        "add_snapshot": add_shapshot,
        "get_snapshots": get_snapshots,
        "plot": plot,
        "pdf": pdf,
    }.get(path)
    if handler:
        return handler(request)
    else:
        return HttpResponse(content='Wrong path: {0}'.format(path), status=404)


class ValidationError(Exception):

    def __init__(self, form):
        self.error = dict((item[0], item[1][0]) for item in form.errors.items())

    def __str__(self):
        return json.dumps(self.error)


def form_validation(method):
    def wrapper(*args, **kargs):
        try:
            response = method(*args, **kargs)
        except Http404, error:
            logger.warn(error)
            return HttpResponse(content=error, status=404)
        except ValidationError, error:
            logger.warn(error)
            return HttpResponse(content=error, status=400)
        except IntegrityError, error:
            logger.warn(error)
            return HttpResponse(content=error, status=400)
        else:
            return response or HttpResponse(content="Success")
    return wrapper


@form_validation
def add_cluster(request):
    form = forms.AddClusterForm(request.POST)
    if form.is_valid():
        form.save()
        if form.cleaned_data.get("master_node"):
            collector = Collector(form.settings)
            for bucket in collector._get_buckets():
                collector.mc.add_bucket(bucket)
            for node in collector._get_nodes():
                collector.mc.add_server(node)
    else:
        raise ValidationError(form)


@form_validation
def add_server(request):
    form = forms.AddServerForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        raise ValidationError(form)


@form_validation
def add_bucket(request):
    form = forms.AddBucketForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        raise ValidationError(form)


@form_validation
def delete_cluster(request):
    cluster = get_object_or_404(models.Cluster, name=request.POST["name"])

    form = forms.DeleteClusterForm(request.POST, instance=cluster)
    if form.is_valid():
        cluster.delete()
    else:
        raise ValidationError(form)


@form_validation
def delete_server(request):
    cluster = get_object_or_404(models.Cluster, name=request.POST["cluster"])
    server = get_object_or_404(models.Server, address=request.POST["address"],
                               cluster=cluster)

    form = forms.DeleteServerForm(request.POST, instance=server)
    if form.is_valid():
        server.delete()
    else:
        raise ValidationError(form)


@form_validation
def delete_bucket(request):
    cluster = get_object_or_404(models.Cluster, name=request.POST["cluster"])
    bucket = get_object_or_404(models.Bucket, name=request.POST["name"],
                               cluster=cluster)

    form = forms.DeleteBucketForm(request.POST, instance=bucket)
    if form.is_valid():
        bucket.delete()
    else:
        raise ValidationError(form)


def get_tree_data(request):
    """"Generate json data for jstree"""
    response = []

    for cluster in models.Cluster.objects.all():
        cluster_obj = {
            "data": cluster.name,
            "attr": {"class": "cluster", "id": cluster.name},
            "children": [
                {"data": "Servers",
                 "attr": {"class": "servers"},
                 "children": []},
                {"data": "Buckets",
                 "attr": {"class": "buckets"},
                 "children": []}]
        }
        for server in models.Server.objects.filter(cluster=cluster):
            server_obj = {
                "data": server.address,
                "attr": {"class": "server", "id": server.address}
            }
            cluster_obj["children"][0]["children"].append(server_obj)
        for bucket in models.Bucket.objects.filter(cluster=cluster):
            bucket_obj = {
                "data": bucket.name,
                "attr": {"class": "bucket", "id": bucket.name},
            }
            cluster_obj["children"][1]["children"].append(bucket_obj)

        response.append(cluster_obj)

    return HttpResponse(content=json.dumps(response))


@form_validation
def get_clusters(request):
    """Get list of active clusters"""
    clusters = [c.name for c in models.Cluster.objects.all()]
    content = json.dumps(sorted(clusters))
    return HttpResponse(content)


@form_validation
def get_servers(request):
    """Get list of active servers for given cluster"""
    form = forms.GetServersForm(request.GET)
    if form.is_valid():
        try:
            cluster = models.Cluster.objects.get(name=request.GET["cluster"])
            servers = models.Server.objects.filter(cluster=cluster).values()
            servers = [s["address"] for s in servers]
        except DoesNotExist:
            servers = []
    else:
        servers = []
    content = json.dumps(sorted(servers))
    return HttpResponse(content)


@form_validation
def get_buckets(request):
    """Get list of active buckets for given server"""
    form = forms.GetBucketsForm(request.GET)
    if form.is_valid():
        try:
            cluster = models.Cluster.objects.get(name=request.GET["cluster"])
            buckets = models.Bucket.objects.filter(cluster=cluster).values()
            buckets = [b["name"] for b in buckets]
        except DoesNotExist:
            buckets = []
    else:
        buckets = []
    content = json.dumps(sorted(buckets))
    return HttpResponse(content)


@form_validation
def get_metrics_and_events(request):
    """Get list of metrics or events for given cluster, server and bucket"""
    form = forms.GetMetricsAndEvents(request.GET)

    if form.is_valid():
        try:
            observables = models.Observable.objects.filter(**form.params).values()
            observables = [{"name": o["name"], "collector": o["collector"]}
                           for o in observables]
        except DoesNotExist:
            observables = []
    else:
        observables = []
    content = json.dumps(sorted(observables))
    return HttpResponse(content)


@form_validation
def add_metric_or_event(request):
    form = forms.AddMetricsAndEvents(request.POST)
    if form.is_valid():
        observable = form.save(commit=False)
        observable.bucket = form.cleaned_data["bucket"]
        observable.server = form.cleaned_data["server"]
        observable.save()
    else:
        raise ValidationError(form)


@form_validation
def add_shapshot(request):
    form = forms.AddSnapshot(request.POST)
    if form.is_valid():
        form.save()
    else:
        raise ValidationError(form)


@form_validation
def get_snapshots(request):
    snapshots = [s.name for s in models.Snapshot.objects.all()]
    content = json.dumps(snapshots)
    return HttpResponse(content)


def plot(request):
    snapshot = request.POST["snapshot"]
    plotter = Plotter()
    response = plotter.plot(snapshot)
    return HttpResponse(content=json.dumps(response))


def pdf(request):
    snapshot = request.POST["snapshot"]
    plotter = Plotter()
    response = plotter.pdf(snapshot)
    return HttpResponse(response)
