"""
urls for networks
"""

from django.conf.urls import patterns, url

from networks import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'network/text/(?P<text_id>.*?)/network/(?P<network_id>.*?)/$', views.text_network, name='text_network'),
    url(r'network/text/(?P<text_id>.*?)/$', views.text_network, name='text_network'),
    url(r'network/(?P<network_id>.*?)/$', views.network_endpoint, name='network_endpoint'),
    url(r'network/$', views.list_networks, name='list_networks'),
    url(r'dataset/(?P<dataset_id>.*?)/$', views.dataset_endpoint, name='dataset_endpoint'),
    url(r'dataset/$', views.list_datasets, name='list_datasets'),
    url(r'node/appellations/(?P<node_id>.*?)/$', views.node_appellations, name='node_appellations'),
    url(r'edge/relations/(?P<edge_id>.*?)/$', views.edge_relations, name='node_appellations'),
    url(r'appellations/(?P<text_id>.*?)/$', views.text_appellations, name='text_appellations'),
    url(r'appellations/$', views.text_appellations, name='all_appellations'),
)