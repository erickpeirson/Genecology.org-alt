"""
urls for networks
"""

from django.conf.urls import patterns, url

from networks import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'(\d+)/$', views.get_network, name='get_network'),
)