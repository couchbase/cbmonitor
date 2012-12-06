from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'/search', 'reports.views.search'),
    url(r'/$', 'reports.views.index'),
)
