from lettuce import before, step, world
from django.test.client import Client
from nose.tools import assert_equals


@before.all
def set_browser():
    world.client = Client()


@step(r'I access the url "(.*)"')
def access_url(step, url):
    world.response = world.client.get(url)


@step(r'I get status code (.*)')
def get_status_code(step, code):
    assert_equals(world.response.status_code, int(code))
