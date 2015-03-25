from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render


import json

from .models import *
from .forms import *

class AccessionInline(admin.TabularInline):
    model = Accession
    extra = 0
    max_num = 0
    
    can_delete = False

    exclude = ( 'label',    )
    readonly_fields = ( 'created', 'appellations', 'relations'  )
    
    def appellations(self, obj):
        return obj.annotation_set.filter(real_type__model='appellation').count()

    def relations(self, obj):
        return obj.annotation_set.filter(real_type__model='relation').count()

class NetworkAdmin(admin.ModelAdmin):
    model = Network
    form = NetworkForm
    inlines = (AccessionInline,)

class AppellationAdmin(admin.ModelAdmin):
    model = Appellation
    readonly_fields = ( 'label', 'in_accession', 'interpretation',
                        'text', 'start_position', 'end_position', 'made_by' )

class RelationAdmin(admin.ModelAdmin):
    model = Relation

    readonly_fields = ( 'label', 'in_accession', 'source', 'predicate',
                        'target', 'start', 'occur', 'end', 'made_by'   )

class LayoutAdmin(admin.ModelAdmin):
    model = Layout
    form = LayoutForm

    def get_urls(self):
        urls = super(LayoutAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^json/(?P<layout_id>.*?)/$', self.layout_json, name='layout-json'),
        )
        return extra_urls + urls

    def layout_json(self, request, layout_id):
        layout = Layout.objects.get(pk=layout_id)
        nodepositions = layout.nodeposition_set.all()
        node_order = { nodepositions[i].describes.id:i for i in xrange(len(nodepositions)) }
        node_positions = { pos.describes.id: {'x':pos.x, 'y':pos.y} for pos in nodepositions }
        response_data = {
            'nodes': [ {
                'label': pos.describes.label,
                'id': pos.describes.id,
                'x': pos.x,
                'y': pos.y,
                } for pos in nodepositions ],
            'edges': [ {
                'source': node_order[edge.source.id],
                'target': node_order[edge.target.id],
                'label': edge.label,
                'x1': node_positions[edge.source.id]['x'],
                'y1': node_positions[edge.source.id]['y'],
                'x2': node_positions[edge.target.id]['x'],
                'y2': node_positions[edge.target.id]['y'],
                } for edge in layout.describes.edge_set.all() ],
            }
        return HttpResponse(    json.dumps(response_data),
                                content_type="application/json" )

class NodeAdmin(admin.ModelAdmin):
    model = Node
    search_fields = ('label',)

admin.site.register(Network, NetworkAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Edge)
admin.site.register(Text)
admin.site.register(Relation, RelationAdmin)
admin.site.register(Appellation, AppellationAdmin)
admin.site.register(Layout, LayoutAdmin)
admin.site.register(NodePosition)