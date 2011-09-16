from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'login/$', 'facebook.views.login_handler'),
    url(r'deauthorize/$', 'facebook.views.deauthorize_handler'),
)
