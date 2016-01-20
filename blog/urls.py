from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # url(r'^blog/', include('blog.urls')),
)

urlpatterns += staticfiles_urlpatterns()
