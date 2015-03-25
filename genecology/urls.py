from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from rest_framework import routers
from main import rest
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'network', rest.NetworkViewSet)
router.register(r'node', rest.NodeViewSet)
router.register(r'edge', rest.EdgeViewSet)
router.register(r'concept', rest.ConceptViewSet)
router.register(r'relation', rest.RelationViewSet)
router.register(r'appellation', rest.AppellationViewSet)
router.register(r'text', rest.TextViewSet)
router.register(r'type', rest.TypeViewSet)
router.register(r'layout', rest.LayoutViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'genecology.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^network/$', 'main.views.display_network'),
    url(r'^text/(?P<text_id>.*?)/$', 'main.views.display_text'),
    url(r'^text/$', 'main.views.list_texts'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^download/network/(?P<network_id>.*?)/$', 'main.views.download_network'),
    url(r'^rest/', include(router.urls)),
    url(r'^rest/auth/', include('rest_framework.urls', namespace='rest_framework'))
)
