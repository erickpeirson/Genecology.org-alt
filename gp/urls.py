import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^browser/', include('browser.urls')),
    url(r'^networks/', include('networks.urls')),
    url(r'^concepts/', include('concepts.urls', namespace='concepts')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
)

urlpatterns += staticfiles_urlpatterns()