from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns(
    'cbmonitor',
    url(r'^$', 'views.index'),
    url(r'^reports/html/', 'views.html_report'),
    url(r'^cbmonitor/(?P<path>[a-z_]+)/$', 'rest_api.dispatcher'),
)
urlpatterns += patterns(
    '',
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^seriesly/(?P<url>.*)$', 'httpproxy.views.proxy'),
)
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT})
    )
