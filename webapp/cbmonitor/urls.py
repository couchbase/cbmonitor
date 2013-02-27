from django.conf.urls import patterns, url

urlpatterns = patterns(
    'cbmonitor',
    url(r'^$', 'views.tab'),
    url(r'^[a-z_]+/$', 'views.tab'),
    url(r'^cbmonitor/(?P<path>[a-z_]+)/$', 'rest_api.dispatcher'),
)
