from django.shortcuts import render_to_response
from django.http import HttpResponse


def main(request, demo):
    if demo == 'flot':
        return flot(request)
    elif demo == 'rickshaw':
        return rickshaw(request)
    elif demo == 'nvd3':
        return nvd3(request)
    elif demo == 'cubism':
        return cubism(request)
    else:
        return HttpResponse(content="Demo doesn't exist", status=404)


def flot(request):
    return render_to_response('flot.html')


def rickshaw(request):
    return render_to_response('rickshaw.html')


def nvd3(request):
    return render_to_response('nvd3.html')


def cubism(request):
    return render_to_response('cubism.html')
