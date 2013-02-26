from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from webapp.cbmonitor.urls import urlpatterns

admin.autodiscover()

urlpatterns += patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^seriesly/(?P<url>.*)$', 'httpproxy.views.proxy'),
    url(r'^litmus/', include('litmus.urls')),
)
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT})
    )
