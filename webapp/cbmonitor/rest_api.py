import json
import logging
import logging.config

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import models

logging.config.fileConfig("logging.conf")
logger = logging.getLogger()


@csrf_exempt
def dispatcher(request, path):
    if path == "add_cluster":
        return add_cluster(request)
    if path == "add_server":
        return add_server(request)
    if path == "add_bucket":
        return add_bucket(request)
    if path == "delete_cluster":
        return delete_cluster(request)
    if path == "delete_server":
        return delete_server(request)
    if path == "delete_bucket":
        return delete_bucket(request)
    if path == "get_tree_data":
        return get_tree_data(request)
    if path == "get_clusters":
        return get_clusters(request)
    if path == "get_servers":
        return get_servers(request)
    if path == "get_buckets":
        return get_buckets(request)
    if path == "get_metrics_and_events":
        return get_metrics_and_events(request)
    else:
        return HttpResponse(content='Wrong path', status=404)


def exception_less(method):
    def wrapper(*args, **kargs):
        try:
            response = method(*args, **kargs)
        except MultiValueDictKeyError, error:
            logger.warn(error)
            return HttpResponse(content="Missing Parameter", status=400)
        except IntegrityError, error:
            logger.warn(error)
            return HttpResponse(content="Duplicate", status=400)
        except ObjectDoesNotExist, error:
            logger.warn(error)
            return HttpResponse(content="Bad Parent", status=400)
        except ValueError, error:
            logger.warn(error)
            return HttpResponse(content="Bad Parameter", status=400)
        else:
            return response or HttpResponse(content="Success")
    return wrapper


@exception_less
def add_cluster(request):
    models.Cluster.objects.create(
        name=request.POST["name"],
        description=request.POST.get("description", "")
    )


@exception_less
def add_server(request):
    cluster = models.Cluster.objects.get(name=request.POST["cluster"])

    if not request.POST.get("ssh_password", "") and \
            not request.POST.get("ssh_key", ""):
        raise MultiValueDictKeyError

    models.Server.objects.create(
        cluster=cluster,
        address=request.POST["address"],
        rest_username=request.POST["rest_username"],
        rest_password=request.POST["rest_password"],
        ssh_username=request.POST["ssh_username"],
        ssh_password=request.POST.get("ssh_password", ""),
        ssh_key=request.POST.get("ssh_key", ""),
        description=request.POST.get("description", "")
    )


@exception_less
def add_bucket(request):
    server = models.Server.objects.get(address=request.POST["server"])
    bucket_type = models.BucketType.objects.get(type=request.POST["type"])

    models.Bucket.objects.create(
        server=server,
        name=request.POST["name"],
        type=bucket_type,
        port=request.POST["port"],
        password=request.POST.get("password", None)
    )


@exception_less
def delete_cluster(request):
    models.Cluster.objects.filter(name=request.POST["name"]).delete()


@exception_less
def delete_server(request):
    models.Server.objects.filter(address=request.POST["address"]).delete()


@exception_less
def delete_bucket(request):
    server = models.Server.objects.get(address=request.POST["server"])
    buckets = models.Bucket.objects.filter(name=request.POST["name"],
                                           server=server)
    buckets.delete()


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


@exception_less
def get_clusters(request):
    """Get list of active clusters"""
    clusters = [c.name for c in models.Cluster.objects.all()]
    return HttpResponse(content=json.dumps(clusters))


@exception_less
def get_servers(request):
    """Get list of active servers for given cluster"""
    cluster = models.Cluster.objects.get(name=request.GET["cluster"])
    servers = [s.address for s in models.Server.objects.filter(cluster=cluster)]
    return HttpResponse(content=json.dumps(servers))


@exception_less
def get_buckets(request):
    """Get list of active buckets for given server"""
    server = models.Server.objects.get(address=request.GET["server"])
    buckets = [b.name for b in models.Bucket.objects.filter(server=server)]
    return HttpResponse(content=json.dumps(buckets))


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
        data = [m.name for m in models.Metric.objects.filter(**params)]
    else:
        data = [e.name for e in models.Event.objects.filter(**params)]

    return HttpResponse(content=json.dumps(data))
