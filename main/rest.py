from django.conf.urls import url, include
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from .models import *
import concepts

from rest_framework import routers, serializers, viewsets, pagination, response
from rest_framework_cj.fields import LinkField
from rest_framework.reverse import reverse

import time

### Serializers ###

class ContextualSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        self.context = kwargs.get('context', None)
        super(ContextualSerializer, self).__init__(*args, **kwargs)

class NetworkListSerializer(ContextualSerializer):
    class Meta:
        model = Network
        fields = ('url', 'label')

class NetworkDetailSerializer(ContextualSerializer):
    edges = LinkField('generate_edges')
    nodes = LinkField('generate_nodes')

    class Meta:
        model = Network
        fields = ('url', 'label', 'nodes', 'edges')
    
    def __init__(self, *args, **kwargs):
        self.context = kwargs.get('context', None)
        super(NetworkDetailSerializer, self).__init__(*args, **kwargs)

    def generate_edges(self, obj):
        qs = Edge.objects.filter(part_of__id=obj.id)
        text = self.context['request'].GET.get('text', None)
        
        if text is not None:
            relations = Relation.objects.filter(predicate__text__id=text)
            qs = [edge for rel in relations for edge in rel.edge_set.all()]
            node_order = { self.nodes[i].id:i for i in xrange(len(self.nodes)) }
        
            return [ {
                'url': reverse(   'edge-detail', args=[edge.id], request=self.context['request'] ),
                'id': edge.id,
                'label': edge.label,
                'source': node_order[edge.source.id],
                'source_id': edge.source.id,
                'target': node_order[edge.target.id],
                'target_id': edge.target.id,
                 }
                        for edge in qs if edge.part_of == obj ]
    
    def generate_nodes(self, obj):
        qs = Node.objects.filter(part_of_id=obj.id)
        text = self.context['request'].GET.get('text', None)
        
        if text is not None:
            appellations = Appellation.objects.filter(text__id=text)
            qs = [node for app in appellations for node in app.node_set.all()]
            self.nodes = qs
            return [ {
                'url': reverse(   'node-detail', args=[node.id], request=self.context['request'] ),
                'id': node.id,
                'label': node.label,
                'concept': node.represents.id,
                }
                        for node in qs if node.part_of == obj ]


class NodeDetailSerializer(ContextualSerializer):
    evidence = LinkField('generate_evidence')

    class Meta:
        model = Node
        fields = ('url', 'label', 'represents', 'evidence', 'part_of')
    
    def generate_evidence(self, obj):
        return [ reverse(   'appellation-detail',
                            args=[ev.cast().id],
                            request=self.context['request'])
                    for ev in obj.evidence.all() ]

class NodeListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Node
        fields  = ('url', 'label')

class EdgeDetailSerializer(ContextualSerializer):
    evidence = LinkField('generate_evidence')

    class Meta:
        model = Edge
        fields =(   'url', 'label', 'source', 'represents', 'target',
                    'evidence', 'part_of')

    def generate_evidence(self, obj):
        return [ reverse(   'relation-detail',
                            args=[ev.cast().id],
                            request=self.context['request'])
                    for ev in obj.evidence.all() ]

class EdgeListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Edge

        fields = ('url','label')

class ConceptListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = concepts.models.Concept
        fields = ('url', 'uri', 'label', 'id')

class ConceptDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = concepts.models.Concept
        fields = ('url', 'uri', 'label', 'typed', 'description', 'resolved')

class TypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = concepts.models.Type
        fields = ('url', 'uri', 'label', 'description', 'resolved')


class RelationListSerializer(ContextualSerializer):
    class Meta:
        model = Relation
        fields = ('url', 'label')

class RelationDetailSerializer(ContextualSerializer):
    class Meta:
        model = Relation
        fields = (  'url', 'label', 'source', 'predicate', 'target', 'start',
                    'occur', 'end'  )


class TextListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Text
        fields = ('url', 'uri', 'content_url', 'label', 'creators', 'restricted', 'length', 'id')

class AppellationListSerializer(ContextualSerializer):
    text = TextListSerializer()
    interpretation = ConceptListSerializer()
    
    class Meta:
        model = Appellation
        fields = ('url', 'label', 'text', 'start_position', 'end_position', 'interpretation')

class AppellationDetailSerializer(ContextualSerializer):
    class Meta:
        model = Appellation
        fields = ('url', 'label', 'start_position', 'end_position', 'text', 'interpretation')


class LayoutListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Layout
        fields = ('url', 'label',)

class LayoutDetailSerializer(serializers.HyperlinkedModelSerializer):
    nodes = LinkField('generate_nodes')
    edges = LinkField('generate_edges')

    class Meta:
        model = Layout
        fields = ('url', 'label', 'nodes', 'edges')
    
    def generate_nodes(self, layout):
        print 'generate_nodes'
        start = time.time()
        self.nodepositions = [ pos for pos in layout.nodeposition_set.all() ]
        print time.time() - start
        node_data = [{
            'label': pos.describes_by_label,
            'id': pos.describes_by_id,
            'concept': pos.describes.represents.id,
            'x': pos.x,
            'y': pos.y,
            } for pos in self.nodepositions ]
        print time.time() - start
        return node_data
    
    def generate_edges(self, layout):
        print 'generate_edges'
        start = time.time()
#        nodepositions = layout.nodeposition_set.prefetch_related('describes').all()
        nodepositions = self.nodepositions
        print time.time() - start
        node_order = { nodepositions[i].describes_by_id:i for i in xrange(len(self.nodepositions)) }
        print time.time() - start
        node_positions = { pos.describes_by_id: {'x':pos.x, 'y':pos.y} for pos in nodepositions }
        print time.time() - start
        edge_data = [ {
            'id': edge.id,
            'source': node_order[edge.source.id],
            'source_id': edge.source.id,
            'target': node_order[edge.target.id],
            'target_id': edge.target.id,
            'label': edge.label,
            'x1': node_positions[edge.source.id]['x'],
            'y1': node_positions[edge.source.id]['y'],
            'x2': node_positions[edge.target.id]['x'],
            'y2': node_positions[edge.target.id]['y'],
            } for edge in layout.describes.edge_set.prefetch_related('source', 'target').all() ]
        print time.time() - start
        return edge_data

### ViewSets ###

class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkListSerializer
    
    def retrieve(self, request, pk=None):
        if pk is not None:
            self.serializer_class = NetworkDetailSerializer
        return super(NetworkViewSet, self).retrieve(request, pk)

class NodeViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeListSerializer
    paginator_class = Paginator
    paginate_by = 20
    paginate_by_param = 'num'
    filter_fields=('part_of',)
    
    def retrieve(self, request, pk=None):
        if pk is not None:
            self.serializer_class = NodeDetailSerializer
        return super(NodeViewSet, self).retrieve(request, pk)

    def get_queryset(self):
        queryset = super(NodeViewSet, self).get_queryset()

        # Now filter by Network, if selected.
        network_id = self.request.QUERY_PARAMS.get('network', None)
        if network_id is not None:
            # If `network=` is given without a value, assign a non-existant int
            #  value so that a 404 is generated.
            try: int(network_id)
            except ValueError: network_id = -1
            queryset = queryset.filter(part_of_id=network_id)

        num = self.request.QUERY_PARAMS.get('num', None)
        if num == 'all':
            self.paginate_by = queryset.count()

        return queryset


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = Edge.objects.all()
    serializer_class = EdgeListSerializer

    paginator_class = Paginator
    paginate_by = 20
    paginate_by_param = 'num'

    def retrieve(self, request, pk=None):
        if pk is not None:
            self.serializer_class = EdgeDetailSerializer
        return super(EdgeViewSet, self).retrieve(request, pk)

    def get_queryset(self):
        queryset = super(EdgeViewSet, self).get_queryset()

        # Now filter by Network, if selected.
        network_id = self.request.QUERY_PARAMS.get('network', None)
        if network_id is not None:
            try:
                int(network_id)
            except ValueError:
                network_id = -1
            queryset = queryset.filter(part_of_id=network_id)
            
        num = self.request.QUERY_PARAMS.get('num', None)
        if num == 'all':
            self.paginate_by = queryset.count()
        
        return queryset


class ConceptViewSet(viewsets.ModelViewSet):
    queryset = concepts.models.Concept.objects.all()
    serializer_class = ConceptListSerializer

    paginator_class = Paginator
    paginate_by = 20
    paginate_by_param = 'num'

    filter_fields = ('uri', 'typed')

    def retrieve(self, request, pk=None):
        if pk is not None:
            self.serializer_class = ConceptDetailSerializer
        return super(ConceptViewSet, self).retrieve(request, pk)

class TypeViewSet(viewsets.ModelViewSet):
    queryset = concepts.models.Type.objects.all()
    serializer_class = TypeSerializer

    paginator_class = Paginator
    paginate_by = 20
    paginate_by_param = 'num'

    filter_fields = ('uri',)    

class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationListSerializer

    paginator_class = Paginator
    paginate_by = 20
    paginate_by_param = 'num'
    
    filter_fields = ('in_accession',)

    def retrieve(self, request, pk=None):
        if pk is not None:
            self.serializer_class = RelationDetailSerializer
        return super(RelationViewSet, self).retrieve(request, pk)

    def get_queryset(self):
        queryset = super(RelationViewSet, self).get_queryset()
            
        num = self.request.QUERY_PARAMS.get('num', None)
        if num == 'all':
            self.paginate_by = queryset.count()
        
        return queryset

class AppellationViewSet(viewsets.ModelViewSet):
    queryset = Appellation.objects.all()
    serializer_class = AppellationListSerializer

    paginator_class = Paginator
    paginate_by = 20
    paginate_by_param = 'num'
    
    filter_fields = ('in_accession','interpretation', 'text')
    
    
    def retrieve(self, request, pk=None):
        if pk is not None:
            self.serializer_class = AppellationDetailSerializer
        return super(AppellationViewSet, self).retrieve(request, pk)

    def get_queryset(self):
        queryset = super(AppellationViewSet, self).get_queryset()
            
        num = self.request.QUERY_PARAMS.get('num', None)
        if num == 'all':
            self.paginate_by = queryset.count()
        
        return queryset

class TextViewSet(viewsets.ModelViewSet):
    queryset = Text.objects.all()
    serializer_class = TextListSerializer
    
    paginator_class = Paginator
    paginate_by = 5
    paginate_by_param = 'num'
    
    filter_fields = ('uri','creators')

    def get_queryset(self):
        queryset = super(TextViewSet, self).get_queryset()
            
        num = self.request.QUERY_PARAMS.get('num', None)
        if num == 'all':
            self.paginate_by = queryset.count()
        
        return queryset

class LayoutViewSet(viewsets.ModelViewSet):
    queryset = Layout.objects.all()
    serializer_class = LayoutListSerializer

    def retrieve(self, request, pk=None):
        if pk is not None:
            self.serializer_class = LayoutDetailSerializer
        return super(LayoutViewSet, self).retrieve(request, pk)

