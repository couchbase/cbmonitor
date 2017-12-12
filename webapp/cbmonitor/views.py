import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page

from cbmonitor import forms
from cbmonitor import models
from cbmonitor.plotter import Plotter

logger = logging.getLogger(__name__)


@cache_page()
def html_report(request):
    """Static HTML reports with PNG charts"""
    try:
        snapshots = parse_snapshots(request)
    except ObjectDoesNotExist:
        return HttpResponse("Wrong or missing snapshot", status=400)

    labels = request.GET.getlist("label")
    if labels and len(labels) != len(snapshots):
        return HttpResponse("Snapshot and labels do not match", status=400)

    plotter = Plotter()
    images = plotter.plot(snapshots, custom_labels=labels)

    def id_from_url(url):
        return url.split("/")[-1].split(".")[0]

    urls = [(id_from_url(url), title, url) for title, url in images]

    if urls:
        return render_to_response("report.html", {"urls": urls})
    else:
        return HttpResponse("No metrics found", status=400)


def parse_snapshots(request):
    snapshots = []
    for snapshot in request.GET.getlist("snapshot"):
        snapshot = models.Snapshot.objects.get(name=snapshot)
        snapshots.append(snapshot)
    return snapshots


class ValidationError(Exception):

    def __init__(self, form):
        self.error = {item[0]: item[1][0] for item in form.errors.items()}

    def __str__(self):
        return json.dumps(self.error)


def validation(method):
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


@validation
def add_cluster(request):
    form = forms.AddClusterForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        raise ValidationError(form)


@validation
def add_server(request):
    form = forms.AddServerForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        raise ValidationError(form)


@validation
def add_bucket(request):
    form = forms.AddBucketForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        raise ValidationError(form)


@validation
def add_index(request):
    form = forms.AddIndexForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        raise ValidationError(form)


def get_clusters(request):
    clusters = [c.name for c in models.Cluster.objects.all()]
    content = json.dumps(sorted(clusters))
    return HttpResponse(content)


@validation
def get_servers(request):
    form = forms.GetServersForm(request.GET)
    if form.is_valid():
        try:
            cluster = models.Cluster.objects.get(name=request.GET["cluster"])
            servers = models.Server.objects.filter(cluster=cluster).values()
            servers = [s["address"] for s in servers]
        except ObjectDoesNotExist:
            servers = []
    else:
        servers = []
    content = json.dumps(sorted(servers))
    return HttpResponse(content)


@validation
def get_buckets(request):
    form = forms.GetBucketsForm(request.GET)
    if form.is_valid():
        try:
            cluster = models.Cluster.objects.get(name=request.GET["cluster"])
            buckets = models.Bucket.objects.filter(cluster=cluster).values()
            buckets = [b["name"] for b in buckets]
        except ObjectDoesNotExist:
            buckets = []
    else:
        buckets = []
    content = json.dumps(sorted(buckets))
    return HttpResponse(content)


@validation
def get_indexes(request):
    form = forms.GetIndexForm(request.GET)
    if form.is_valid():
        try:
            cluster = models.Cluster.objects.get(name=request.GET["cluster"])
            indexes = models.Index.objects.filter(cluster=cluster).values()
            indexes = [i["name"] for i in indexes]
        except ObjectDoesNotExist:
            indexes = []
    else:
        indexes = []
    content = json.dumps(sorted(indexes))
    return HttpResponse(content)


@validation
def get_metrics(request):
    form = forms.GetMetrics(request.GET)

    if form.is_valid():
        try:
            observables = models.Observable.objects.filter(**form.params).values()
            observables = [{"name": o["name"], "collector": o["collector"]}
                           for o in observables]
        except ObjectDoesNotExist:
            observables = []
    else:
        observables = []
    content = json.dumps(sorted(observables))
    return HttpResponse(content)


@validation
def add_metric(request):
    form = forms.AddMetric(request.POST)
    if form.is_valid():
        observable = form.save(commit=False)
        observable.bucket = form.cleaned_data["bucket"]
        observable.index = form.cleaned_data["index"]
        observable.server = form.cleaned_data["server"]
        observable.save()
    else:
        raise ValidationError(form)


@validation
def add_snapshot(request):
    form = forms.AddSnapshot(request.POST)
    if form.is_valid():
        form.save()
    else:
        raise ValidationError(form)


def get_snapshots(request):
    cluster = request.GET["cluster"]
    snapshots = models.Snapshot.objects.filter(cluster=cluster).values()
    snapshots = [snapshot["name"] for snapshot in snapshots]
    snapshots.insert(0, "all_data")
    content = json.dumps(snapshots)
    return HttpResponse(content)
