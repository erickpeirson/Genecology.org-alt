from django.conf.urls import patterns, url

from locations import views

urlpatterns = patterns('',
    url(r'^retrieve/(?P<uri>.*?)/$', views.retrieve, name='retrieve'),
)