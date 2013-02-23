from django.conf.urls import patterns, url

urlpatterns = patterns(
    'cbmonitor',
    url(r'^$', 'views.index'),
    url(r'^snapshots$', 'views.snapshots'),
    url(r'^cbmonitor/(?P<path>[a-z_]+)/$', 'rest_api.dispatcher'),
)
