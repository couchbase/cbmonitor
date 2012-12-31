import json
import logging
import logging.config

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

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
    server = get_object_or_404(models.Server, address=request.POST["server"])
    bucket = get_object_or_404(models.Bucket, name=request.POST["name"],
                               server=server)

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
            "children": []
        }
        for server in models.Server.objects.filter(cluster=cluster):
            server_obj = {
                "data": server.address,
                "attr": {"class": "server", "id": server.address},
                "children": []
            }
            for bucket in models.Bucket.objects.filter(server=server):
                bucket_obj = {
                    "data": bucket.name,
                    "attr": {"class": "bucket", "id": bucket.name},
                }
                server_obj["children"].append(bucket_obj)
            cluster_obj["children"].append(server_obj)
        response.append(cluster_obj)

    return HttpResponse(content=json.dumps(response))


@form_validation
def get_clusters(request):
    """Get list of active clusters"""
    clusters = models.Cluster.objects.values("name").get()
    content = json.dumps(clusters.values())
    return HttpResponse(content)


@form_validation
def get_servers(request):
    """Get list of active servers for given cluster"""
    form = forms.GetServersForm(request.GET)
    if form.is_valid():
        cluster = get_object_or_404(models.Cluster, name=request.GET["cluster"])
        servers = models.Server.objects.values("address").get(cluster=cluster)
        content = json.dumps(servers.values())
        return HttpResponse(content)
    else:
        raise ValidationError(form)


@form_validation
def get_buckets(request):
    """Get list of active buckets for given server"""
    form = forms.GetBucketsForm(request.GET)
    if form.is_valid():
        server = get_object_or_404(models.Server, address=request.GET["server"])
        buckets = models.Bucket.objects.values("name").get(server=server)
        content = json.dumps(buckets.values())
        return HttpResponse(content)
    else:
        raise ValidationError(form)


def get_metrics_and_events(request):
    """Get list of metrics or events for given cluster, server and bucket"""
    params = {"cluster": request.GET["cluster"]}

    server = request.GET.get("server", None)
    if server:
        params.update({"server": server})
    else:
        params.update({"server__isnull": True})

    bucket = request.GET.get("bucket", None)
    if bucket:
        params.update({"bucket": bucket})
    else:
        params.update({"bucket__isnull": True})

    if request.GET["type"] == "metric":
        data = models.Metric.objects.values("name").get(**params)
    else:
        data = models.Event.objects.values("name").get(**params)
    content = json.dumps(data.values())

    return HttpResponse(content)
