from django.contrib import admin
from networks.models import Network, Node, Edge, TextPosition, Appellation, \
                            Relation, Dataset, NetworkLink, NetworkProjection
from networks.forms import DatasetAdminForm
from django.forms.models import inlineformset_factory

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class NetworkLinkInline(admin.TabularInline):
    model = NetworkLink
    extra = 1

class NetworkAdmin(admin.ModelAdmin):
    """
    adds a new network
    """

    exclude = [ 'nodes', 'edges']
    inlines = [ NetworkLinkInline,]

class DatasetAdmin(admin.ModelAdmin):
    """
    adds a new dataset
    
    specify network
    specify format

    """

    form = DatasetAdminForm
    inlines = [ NetworkLinkInline, ]


admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Node)
admin.site.register(Edge)
admin.site.register(Appellation)
admin.site.register(Relation)
admin.site.register(NetworkProjection)