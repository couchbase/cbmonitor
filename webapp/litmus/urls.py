from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'dashboard/$', 'litmus.views.dashboard'),
    url(r'post/$', 'litmus.views.post'),
    url(r'get/$', 'litmus.views.get'),
)
