import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from models import Cluster, Server, Bucket, BucketType


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
    else:
        return HttpResponse(content='Wrong path', status=404)


def exception_less(method):
    def wrapper(*args, **kargs):
        try:
            response = method(*args, **kargs)
        except MultiValueDictKeyError:
            return HttpResponse(content="Missing Parameter", status=400)
        except IntegrityError:
            return HttpResponse(content="Duplicate", status=400)
        except ObjectDoesNotExist:
            return HttpResponse(content="Bad Parent", status=400)
        except ValueError:
            return HttpResponse(content="Bad Parameter", status=400)
        else:
            return response or HttpResponse(content="Success")
    return wrapper


@exception_less
def add_cluster(request):
    Cluster.objects.create(
        name=request.POST["name"],
        description=request.POST.get("description", "")
    )


@exception_less
def add_server(request):
    cluster = Cluster.objects.get(name=request.POST["cluster"])

    if not request.POST.get("ssh_password", "") and \
            not request.POST.get("ssh_key", ""):
        raise MultiValueDictKeyError

    Server.objects.create(
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
    server = Server.objects.get(address=request.POST["server"])
    bucket_type = BucketType.objects.get(type=request.POST["type"])

    Bucket.objects.create(
        server=server,
        name=request.POST["name"],
        type=bucket_type,
        port=request.POST["port"],
        password=request.POST.get("password", None)
    )


@exception_less
def delete_cluster(request):
    Cluster.objects.filter(name=request.POST["name"]).delete()


@exception_less
def delete_server(request):
    Server.objects.filter(address=request.POST["address"]).delete()


@exception_less
def delete_bucket(request):
    server = Server.objects.get(address=request.POST["server"])
    buckets = Bucket.objects.filter(name=request.POST["name"], server=server)
    buckets.delete()


def get_tree_data(request):
    """"Generate json data for jstree"""
    response = []

    for cluster in Cluster.objects.all():
        cluster_obj = {
            "data": cluster.name,
            "attr": {"class": "cluster", "id": cluster.name},
            "children": []
        }
        for server in Server.objects.filter(cluster=cluster):
            server_obj = {
                "data": server.address,
                "attr": {"class": "server", "id": server.address},
                "children": []
            }
            for bucket in Bucket.objects.filter(server=server):
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
    clusters = [c.name for c in Cluster.objects.all()]
    return HttpResponse(content=json.dumps(clusters))


@exception_less
def get_servers(request):
    """Get list of active servers for given cluster"""
    cluster = Cluster.objects.get(name=request.GET["cluster"])
    servers = [s.address for s in Server.objects.filter(cluster=cluster)]
    return HttpResponse(content=json.dumps(servers))


@exception_less
def get_buckets(request):
    """Get list of active servers for given cluster"""
    server = Server.objects.get(address=request.GET["server"])
    buckets = [b.name for b in Bucket.objects.filter(server=server)]
    return HttpResponse(content=json.dumps(buckets))
