from django.shortcuts import render_to_response


def demo_flot(request):
    return render_to_response('demo_flot.html')


def demo_rickshaw(request):
    return render_to_response('demo_rickshaw.html')
