from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^seriesly/(?P<url>.*)$', 'httpproxy.views.proxy'),
    url(r'^demo-flot/$', 'webapp.views.demo_flot', name='demo_flot'),
    url(r'^demo-rickshaw/$', 'webapp.views.demo_rickshaw', name='demo_rickshaw'),
    url(r'^cbdata/$', 'webapp.views.cbdata', name='cbdata'),
    url(r'^demo-nvd3/$', 'webapp.views.demo_nvd3', name='demo_nvd3'),
    url(r'^demo-cubism/$', 'webapp.views.demo_cubism', name='demo_cubism'),
    url(r'^litmus/$', 'webapp.views.litmus', name='litmus'),
)
