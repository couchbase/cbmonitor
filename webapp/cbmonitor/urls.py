from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'cbmonitor.views.index'),
    url(r'/(?P<path>[a-z_]+)/$', 'cbmonitor.rest_api.dispatcher'),
)
