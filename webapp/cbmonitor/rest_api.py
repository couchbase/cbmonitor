import json
import logging
import logging.config

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist as DoesNotExist

import models
import forms

logging.config.fileConfig("webapp/logging.conf")
logger = logging.getLogger()


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
        "get_metrics_and_events": get_metrics_and_events
    }.get(path)
    if handler:
        return handler(request)
    else:
        return HttpResponse(content='Wrong path', status=404)


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
        else:
            return response or HttpResponse(content="Success")
    return wrapper


@form_validation
def add_cluster(request):
    form = forms.AddClusterForm(request.POST)
    if form.is_valid():
        form.save()
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
    server = get_object_or_404(models.Server, address=request.POST["address"])

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
    content = json.dumps(clusters)
    return HttpResponse(content)


@form_validation
def get_servers(request):
    """Get list of active servers for given cluster"""
    form = forms.GetServersForm(request.GET)
    if form.is_valid():
        try:
            cluster = models.Cluster.objects.get(name=request.GET["cluster"])
            servers = models.Server.objects.\
                values("address").get(cluster=cluster).values()
        except DoesNotExist:
            servers = []
    else:
        servers = []
    content = json.dumps(servers)
    return HttpResponse(content)


@form_validation
def get_buckets(request):
    """Get list of active buckets for given server"""
    form = forms.GetBucketsForm(request.GET)
    if form.is_valid():
        try:
            cluster = models.Cluster.objects.get(name=request.GET["cluster"])
            buckets = models.Bucket.objects.\
                values("name").get(cluster=cluster).values()
        except DoesNotExist:
            buckets = []
    else:
        buckets = []
    content = json.dumps(buckets)
    return HttpResponse(content)


@form_validation
def get_metrics_and_events(request):
    """Get list of metrics or events for given cluster, server and bucket"""
    form = forms.GetMetricsAndEvents(request.GET)

    if form.is_valid():
        try:
            if form.cleaned_data["type"] == "metric":
                data = models.Observable.objects.values("name").get(**form.params)
            else:
                data = models.Observable.objects.values("name").get(**form.params)
            content = json.dumps(data.values())
        except DoesNotExist:
            content = json.dumps([])
    else:
        content = json.dumps([])
    return HttpResponse(content)
