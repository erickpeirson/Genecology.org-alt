from django.conf.urls import patterns, url

from browser import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'geographic', views.geographic, name='geographic'),
)