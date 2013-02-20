import requests
import ujson


def post_request(request):
    def wrapper(*args, **kargs):
        url, params = request(*args, **kargs)
        r = requests.post(url, params)
        if r.status_code == 500:
            raise Exception("Internal server error")
    return wrapper


def json(method):
    def wrapper(*args, **kargs):
        response = method(*args, **kargs)
        return ujson.loads(response.text)
    return wrapper
