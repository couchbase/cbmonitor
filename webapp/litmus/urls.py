from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'dashboard/$', 'litmus.views.dashboard'),
    url(r'post/$', 'litmus.views.post'),
    url(r'get$', 'litmus.views.get'),
    url(r'post/comment/$', 'litmus.views.post_comment'),
    url(r'get/comment$', 'litmus.views.get_comment'),
    url(r'get/settings$', 'litmus.views.get_settings'),
    url(r'get/tags$', 'litmus.views.get_tags'),
    url(r'post/color/$', 'litmus.views.post_color'),
    url(r'get/color$', 'litmus.views.get_color')
)
