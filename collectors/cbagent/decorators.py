import requests
import ujson

from cbagent.logger import logger


def post_request(request):
    def wrapper(*args, **kargs):
        url, params = request(*args, **kargs)
        try:
            r = requests.post(url, params)
        except requests.exceptions.ConnectionError:
            logger.interrupt("Connection error: {0}".format(url))
        else:
            if r.status_code == 500:
                logger.interrupt("Internal server error: {0}".format(url))
    return wrapper


def json(method):
    def wrapper(*args, **kargs):
        response = method(*args, **kargs)
        return ujson.loads(response.text)
    return wrapper
