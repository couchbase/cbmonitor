from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'dashboard/$', 'webapp.litmus.views.dashboard'),
    url(r'post/$', 'webapp.litmus.views.post'),
    url(r'get/$', 'webapp.litmus.views.get'),
)
