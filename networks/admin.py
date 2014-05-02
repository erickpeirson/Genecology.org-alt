from django.contrib import admin
from networks.models import Network, Node, Edge, TextPosition, Appellation, \
                            Relation, Dataset, NetworkLink, NetworkProjection, \
                            NodeType, ProjectionMapping, Layout, NodePosition

from networks.forms import DatasetAdminForm, LayoutAdminForm
from django.forms.models import inlineformset_factory

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class NetworkLinkInline(admin.TabularInline):
    model = NetworkLink
    extra = 1

class NetworkAdmin(admin.ModelAdmin):
    exclude = [ 'nodes', 'edges']
    inlines = [ NetworkLinkInline,]

class DatasetAdmin(admin.ModelAdmin):
    form = DatasetAdminForm
    inlines = [ NetworkLinkInline, ]

class LayoutAdmin(admin.ModelAdmin):
    form = LayoutAdminForm

class NodePositionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'x', 'y')

#class NetworkProjectionAdmin(admin.ModelAdmin):
#    inlines = [ ProjectionMappingInline, ]


admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Node)
admin.site.register(Edge)
admin.site.register(Appellation)
admin.site.register(Relation)
admin.site.register(NodeType)
admin.site.register(NetworkProjection)#, NetworkProjectionAdmin)
admin.site.register(ProjectionMapping)
admin.site.register(Layout, LayoutAdmin)
admin.site.register(NodePosition, NodePositionAdmin)