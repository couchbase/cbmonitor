import inspect

from django.shortcuts import render_to_response


def tab(request, path=None):
    tab_name = {
        None: "inventory",
        "charts": "charts",
        "snapshots": "snapshots"
    }.get(path)
    template = "{0}/{0}".format(tab_name) + ".jade"
    return render_to_response(template, {tab_name: True})
