from django.conf.urls import patterns, url, include

from concepts import views

urlpatterns = patterns('', 
    url(r'^retrieve/(?P<uri>.*?)/$', views.retrieve, name='retrieve'),
)