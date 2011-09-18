from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_custom_auths.views.home', name='home'),
    # url(r'^django_custom_auths/', include('django_custom_auths.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'account.views.index'),
    url(r'^login/$', 'account.views.login_handler'),
    url(r'^logout/$', 'account.views.logout_handler'),
    url(r'^facebook/', include('facebook.urls')),
    url(r'^googleplus/', include('googleplus.urls')),
)
