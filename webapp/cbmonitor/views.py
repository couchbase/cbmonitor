from django.shortcuts import render_to_response


def index(request):
    data = {"index": True, "snapshots": False}
    return render_to_response("index.jade", data)


def snapshots(request):
    data = {"index": False, "snapshots": True}
    return render_to_response("snapshots.jade", data)
