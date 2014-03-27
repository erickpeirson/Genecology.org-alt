"""
urls for networks
"""

from django.conf.urls import patterns, url

from networks import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'network/(?P<network_id>.*?)/$', views.network_endpoint, name='network_endpoint'),
    url(r'dataset/(?P<dataset_id>.*?)/$', views.dataset_endpoint, name='dataset_endpoint'),
)