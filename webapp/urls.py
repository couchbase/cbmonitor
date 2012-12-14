from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', include('cbmonitor.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^seriesly/(?P<url>.*)$', 'httpproxy.views.proxy'),
    url(r'^demos/(?P<demo>.*)/$', 'demos.views.main'),
    url(r'^litmus/', include('litmus.urls')),
    url(r'^reports', include('reports.urls')),
    url(r'^cbmonitor', include('cbmonitor.urls')),
)
