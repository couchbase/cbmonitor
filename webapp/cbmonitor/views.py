from django.shortcuts import render_to_response

import models


def index(request):
    clusters = [c for c in models.Cluster.objects.all()]
    try:
        servers = [c for c in models.Server.objects.filter(cluster=clusters[0])]
    except IndexError:
        servers = []
    try:
        buckets = [b for b in models.Bucket.objects.filter(server=servers[0])]
    except IndexError:
        buckets = []

    data = {
        "clusters": [c.name for c in clusters],
        "servers": [s.address for s in servers],
        "buckets": [b.name for b in buckets]
    }

    return render_to_response("index.jade", data)
