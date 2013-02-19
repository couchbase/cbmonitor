import requests
import ujson


def post_request(request):
    def wrapper(*args, **kargs):
        url, params = request(*args, **kargs)
        requests.post(url, params)
    return wrapper


def json(method):
    def wrapper(*args, **kargs):
        response = method(*args, **kargs)
        return ujson.loads(response.text)
    return wrapper
