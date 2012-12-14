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
    else:
        return HttpResponse(content='Wrong path', status=404)


def exception_less(method):
    def wrapper(*args, **kargs):
        try:
            method(*args, **kargs)
        except MultiValueDictKeyError:
            return HttpResponse(content="Missing Parameter", status=400)
        except IntegrityError:
            return HttpResponse(content="Duplicate", status=400)
        except ObjectDoesNotExist:
            return HttpResponse(content="Bad Parent", status=400)
        except ValueError:
            return HttpResponse(content="Bad Parameter", status=400)
        else:
            return HttpResponse(content="Success")
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
