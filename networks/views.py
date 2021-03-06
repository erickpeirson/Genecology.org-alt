"""
Provides JSON data about various elements in :mod:`.networks.models`\.

.. autosummary::

   json_response
   node_data
   edge_data
   relation_data
   layout_endpoint
   layout_data
   dataset_endpoint
   network_data
   network_endpoint
   download_network
   network_projection
   list_datasets
   list_networks
   text_appellations
   text_network
   node_appellations
   edge_relations

"""

from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from networks.models import Network, Node, Edge, Dataset, Appellation, \
                            Relation, NetworkProjection, Layout
from networks.writers import GraphMLWriter, flatten

import simplejson
from pprint import pprint

def index(request): # TODO: get rid of this.
    return HttpResponse('Woohoo!')

def json_response(response_data):
    """
    Yields JSON data from a dictionary.
    
    Parameters
    ----------
    response_data : dict
        A dictionary containing some data.
    
    Returns
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.
    """

    response_json = simplejson.dumps(response_data)
    return HttpResponse(response_json, 'application/json')

def appellation_data(appellations):
    """
    Yields a nested dictionary describing a list of :class:`.Appellation`\.
    
    Parameters
    ----------
    appellations : list
        A list of :class:`.Appellation`\.
        
    Returns
    -------
    app_dict : dict
        A nested dictionary describing a list of :class:`.Appellation`\.
    """

    app_data = []
    for app in appellations:
        ad = { 'concept': app.concept.uri,
               'type': app.concept.type.uri,
               'id': app.id     }
        if app.textposition is not None:
            ad['textposition'] = {
                'text_id': app.textposition.text.id,
                'text_title': app.textposition.text.title,
                'text': app.textposition.text.uri,
                'startposition': app.textposition.startposition,
                'endposition': app.textposition.endposition }
        app_data.append(ad)
    app_dict = {'appellations': app_data}
    
    return app_dict

def node_data(nodes):
    """
    Yields a nested dictionary describing a list of :class:`.Node`\.
    
    Parameters
    ----------
    nodes : list
        A list of :class:`.Node`\.
        
    Returns
    -------
    node_data : dict
        A nested dictionary describing a list of :class:`.Node`\.        
    """
    node_data = []
    for node in nodes:
        nd = {  'concept': node.concept.uri,
                'id': node.id,
                'type': node.type.uri,
                'label': node.concept.name,
                'appellations': [ a.id for a in node.appellations.all() ]
                }
        try:
            nd['geographic'] = { 'latitude': node.concept.location.latitude,
                                 'longitude': node.concept.location.longitude }
        except AttributeError:
            pass
        node_data.append(nd)

    return node_data

def edge_data(edges):
    """
    Yields a list of dictionaries describing a list of :class:`.Node`\.
    
    Parameters
    ----------
    edges : list
        A list of :class:`.Edge`\.
        
    Returns
    -------
    edge_data : list
        A list of dictionaries describing a list of :class:`.Edge`\.        
    """
    return [ {  'source': edge.source.id,
                'target': edge.target.id,
                'id': edge.id,
                'concept': edge.concept.uri,
                'label': edge.concept.name,
                'relations': [ r.id for r in edge.relations.all() ]
                } for edge in edges ]

def relation_data(relations):
    """
    Yields a nested dictionary describing a list of :class:`.Relation`\.
    
    Parameters
    ----------
    relations : list
        A list of :class:`.Relation`\.
        
    Returns
    -------
    rel_dict : dict
        A nested dictionary describing a list of :class:`.Relation`\.        
    """
    rel_data = []
    for rel in relations:
        rd = {  'id': rel.id,
                'source': rel.source.id,
                'target': rel.target.id,
                'predicate': { 'id': rel.predicate.id }}
        for field in [ 'startposition', 'endposition' ]:
            try:
                rd['predicate'][field] = rel.predicate.textposition.__dict__[field]
            except (KeyError, AttributeError):
                pass
        try:
            rd['predicate']['text'] = rel.predicate.textposition.text.uri
            rd['predicate']['text_id'] = rel.predicate.textposition.text.id
            rd['predicate']['text_title'] = rel.predicate.textposition.text.title
        except AttributeError:
            pass
        rel_data.append(rd)
    rel_dict = {'relations': rel_data}
    return rel_dict

def layout_endpoint(request, layout_id):
    """
    Provides JSON describing :class:`.Node` and :class:`.Edge` positions.
    
    Parameters
    ----------
    layout_id : int
        Identifier for a :class:`.NetworkLayout`\.

    Returns
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.    
    """

    layout = get_object_or_404(Layout, pk=layout_id)

    response_data = layout_data(layout)

    return json_response(response_data)

def layout_data(layout):
    """
    Yields a dictionary of :class:`.Node` positions.
    
    Parameters
    ----------
    layout :
        A :class:`.NetworkLayout` instance.
        
    Returns
    -------
    postitions: dict
        A nested dictionary of x and y coordinates, indexed on :class:`.Node` id.
    """

    positions = { n.node.id:{'x':n.x, 'y':n.y} for n in layout.positions.all() }
    return positions

def dataset_endpoint(request, dataset_id):
    """
    Provides JSON describing :class:`.Appellation` and :class:`.Relation` for a
    specified dataset.
    
    Parameters
    ----------
    dataset_id : int
        An identifier for a :class:`.Dataset`\.
    
    Returns
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.  
    """

    dataset = get_object_or_404(Dataset, pk=dataset_id)
    
    # Build appellation response.
    app_data = appellation_data(dataset.appellations.all())
    
    # Build relation response.
    rel_data = relation_data(dataset.relations.all())

    # Put it all together.
    response_data = { 'dataset': { 
                        'id': dataset.id,
                        'name': dataset.name,
                        'added': str(dataset.added),
                        'networks': [n.id for n in dataset.networks.all()],
                        'appellations': app_data['appellations'],
                        'relations': rel_data }}

    # And we're done.
    return json_response(response_data)

def network_data(network_id):
    """
    Generates data about :class:`.Node` and :class:`.Edge` for a given
    :class:`.Network`\.
    
    Used primarily by :func:`.network_endpoint`\.
    
    Parameters
    ----------
    network_id : int
        Identifier for a :class:`.Network`\.
    
    Returns
    -------
    response_data : dict
        A nested dictionary describing :class:`.Node` and :class:`.Edge`\.
    """
    network = get_object_or_404(
                Network.objects.prefetch_related('nodes', 'edges',
                                                 'nodes__concept',
                                                 'nodes__concept__location',
                                                 'nodes__type',
                                                 'nodes__appellations',
                                                 'edges__source',
                                                 'edges__target',
                                                 'edges__concept',
                                                 'edges__relations'),
                pk=network_id )
    
    # Build node response.
    n_data = node_data(network.nodes.all())
    
    # Build edge response.
    e_data = edge_data(network.edges.all())

    # Put it all together.
    response_data = { 'network': {
                        'id': network.id,
                        'name': network.name,
                        'nodes': n_data,
                        'edges': e_data  }}

    return response_data

def network_endpoint(request, network_id):
    """
    Provides JSON describing Nodes and Edges for a specified Network.

    Parameters
    ----------
    network_id : int
        Identifier for a :class:`.Network`\.   
        
    Returns    
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.            
    """
    return json_response(network_data(network_id))

def download_network(request, network_id, format='graphml', projection=None):
    """
    Provides an XML representation of a network for download.
    
    Parameters
    ----------
    network_id : int
        An identifier for :class:`.Network`\.
    format : str
        (default: "graphml") The output format for the network.
        
    Returns
    -------
    HttpResponse
        A Django :class:`.HttpResponse` object containing ``application/xml``.
    """
    import networkx as nx
    from xml.etree import cElementTree as ET
                
    data = network_data(network_id)
    
    # Build graph.
    edges = data['network']['edges']
    nodes = data['network']['nodes']
    G = nx.Graph([ (e['source'], e['target'], flatten(e)) for e in edges ])
    G.add_nodes_from([ (n['id'], flatten(n)) for n in nodes ])
    
    writer = GraphMLWriter(encoding='utf-8',prettyprint=True)
    writer.add_graph_element(G)
    writer.indent(writer.xml)
    
    stream = '<?xml version="1.0" encoding="%s"?>'%writer.encoding
    stream += ET.tostring(writer.xml, encoding=writer.encoding)

    response = HttpResponse(stream, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="network_'+network_id+'.graphml'
    return response
    
def network_projection(request, network_id, projection_id):
    """
    Provides JSON data about a :class:`.Network` that has been recast using a
    :class:`.NetworkProjection`\.
    
    Parameters
    ----------
    network_id : int
        An identifier for a :class:`.Network`\.
    projection_id : int
        An identifier for a :class:`.NetworkProjection`\.
    
    Returns    
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.   
    """
    def project_edge(edge, projection):
        for mapping in projection.mappings.all():
            if edge.source.type in mapping.secondaryNodes.all() \
                                    and edge.target.type == mapping.primaryNode:
                return { 'node': edge.source,
                         'secondary': edge.target }
            elif edge.target.type in mapping.secondaryNodes.all() \
                                    and edge.source.type == mapping.primaryNode:
                return { 'node': edge.source,
                         'secondary': edge.target }
        return None

    projection = get_object_or_404(NetworkProjection.objects.prefetch_related('mappings', 'mappings__secondaryNodes'), pk=projection_id)
    node_types = [ p.primaryNode for p in projection.mappings.all() ]

    # Generate node mappings based on projection.
    edges = Edge.objects.prefetch_related('source','target', 
                                          'source__concept',
                                          'target__concept',
                                          'source__concept__location',
                                          'target__concept__location',
                                          'relations',
                                          'concept' ).all()

    node_mappings = {}
    node_contains = {}
    for e in edges:
        map = project_edge(e, projection)
        if map is not None:
            try:
                node_mappings[map['secondary'].id] += [ map['node'].id ]
            except (KeyError, TypeError):
                node_mappings[map['secondary'].id] = [map['node'].id]

            try:
                node_contains[map['node'].id] += [ map['secondary'] ]
            except (KeyError, TypeError):
                node_contains[map['node'].id] = [map['secondary']]

    # Generate a new edge list based on node mappings.
    c_nodes = {}
    c_edges = {}
    node_index = {}
    include_nodes = set([])
    for e in edges:
        collapsed = None
        try:
            source = node_mappings[e.source.id][0]
            try:    # look in the index first.
                source_node = node_index[source]
            except KeyError:
                source_node = Node.objects.get(pk=source)
            collapsed = 'source'
            
            # Update primary node.
            try:
                c_nodes[e.target.id]['contains'] += [source]
            except KeyError:
                c_nodes[e.target.id] = { 'contains': [source] }

        except KeyError:    # No mapping defined for source node.
            source = e.source.id
            source_node = e.source

        try:
            target = node_mappings[e.target.id][0]

            try:    # look in the index first.
                target_node = node_index[target]
            except KeyError:
                target_node = Node.objects.get(pk=target)
            collapsed = 'target'
            
            # Update primary node.
            try:
                c_nodes[e.source.id]['contains'] += [target]
            except KeyError:
                c_nodes[e.source.id] = { 'contains': [target] }
        except KeyError:    # No mapping defined for target node.
            target = e.target.id
                    
        node_index[source] = source_node    # Update index.
        node_index[target] = target_node    # Update index.            

        # Only include edges between primaryNodes in the Projection.
        # TODO: Handle case where source or target has no location.
        if source_node.type in node_types\
                            and target_node.type in node_types:
            if collapsed is not None:
                org = e
            else:
                org = None
            
            f_key = (source, target, e.concept.uri)
            r_key = (target, source, e.concept.uri)
            
            novel = False
            if not c_edges.has_key(f_key) and not c_edges.has_key(r_key):
                novel = True
                
            if novel:
                try:
                    new_edge = {
                        'source': source,
                        'target': target,
                        'id': e.id,
                        'concept': e.concept.uri,
                        'label': e.concept.name,
                        'relations': [ r.id for r in e.relations.all() ],
                        'geographic': {
                            'source': {
                                'latitude': source_node.concept.location.latitude,
                                'longitude': source_node.concept.location.longitude
                            },
                            'target': {
                                'latitude': target_node.concept.location.latitude,
                                'longitude': target_node.concept.location.longitude
                            }
                        },
                        'contains': edge_data([org])
                    }
                    c_edges[f_key] = new_edge                    
                except AttributeError:  # No location data.
                    pass
                

                
                include_nodes.add(source)
                include_nodes.add(target)
            
    all_nodes = [ node_index[id] for id in include_nodes ]
    n_data = node_data(all_nodes)
    for i in xrange(len(n_data)):
        n_data[i]['contains'] = node_data(node_contains[n_data[i]['id']])

    return json_response({'network': {'edges': c_edges.values(), 'nodes': n_data }})

def list_datasets(request):
    """
    Provides a list of all :class:`.Dataset` in JSON.
    
    Returns    
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.  
    """

    datasets = Dataset.objects.all()

    response_data = { 'datasets': [ {
                        'id': dataset.id,
                        'name': dataset.name,
                        'appellations': len(dataset.appellations.all()),
                        'relations': len(dataset.relations.all()),
                        'networks': [ n.id for n in dataset.networks.all() ],
                        'added': str(dataset.added) }
                                    for dataset in datasets ] }

    return json_response(response_data)

def list_networks(request):
    """
    Provides a list of all :class:`.Network` in JSON.
    
    Returns    
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.      
    """

    networks = Network.objects.all()

    response_data = { 'networks': [ {
                        'id': network.id,
                        'name': network.name,
                        'nodes': len(network.nodes.all()),
                        'edges': len(network.edges.all()) }
                                    for network in networks ] }

    return json_response(response_data)

def text_appellations(request, text_id=None): #, dataset_id=None, network_id=None):
    """
    Provides a list of all :class:`.Appellation`\, optionally filtered by
    :class:`.Text`\.

    Parameters
    ----------
    text_id : int
        (optional) An identifier for a :class:`.Text`\.
    
    Returns    
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.      
    """

    appellations = Appellation.objects.select_related('textposition',
                                                      'textposition__text').all()
    relations = Relation.objects.select_related('textposition',
                                                'textposition__text').all()
    
    if text_id is not None:
        appellations = appellations.filter(textposition__text__id=text_id)
        relations = relations.filter(predicate__textposition__text__id=text_id)
    
    # Build appellation response.
    return json_response(dict(appellation_data(appellations).items() + relation_data(relations).items()))

def text_network(request, text_id=None, network_id=None):
    """
    Provides JSON data about :class:`.Node` and :class:`.Edge` rooted in a
    :class:`.Text`\.

    Parameters
    ----------
    text_id : int
        (optional) An identifier for a :class:`.Text`\.    
    network_id : int
        (optional) An identifier for a :class:`.Network`\.
    
    Returns    
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.      
    """

    relations = Relation.objects.filter(predicate__textposition__text__id=text_id)
    appellations = Appellation.objects.filter(textposition__text__id=text_id)
    
    nodes = set(Node.objects.filter(appellations__id__in=[ a.id for a in appellations] ))
    edges = set(Edge.objects.filter(relations__id__in=[ r.id for r in relations ]))
    
    if network_id is not None:
        nodes = nodes.filter(network__id=network_id)
        edges = edges.filter(network__id=network_id)
    
    rdata = { 'network': {
                    'edges': edge_data(edges),
                    'nodes': node_data(nodes),
                    'appellations': appellation_data(appellations),
                    'relations': relation_data(relations) } }
    
    return json_response(rdata)


def node_appellations(request, node_id):
    """
    Provides JSON data about all :class:`.Appellation` for a given 
    :class:`.Node`\.
    
    Parameters
    ----------
    node_id : int
        An identifier for :class:`.Node`\.

    Returns    
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.      
    """
    node = get_object_or_404(Node, pk=node_id)
    return json_response(appellation_data(node.appellations.all()))

def edge_relations(request, edge_id):
    """
    Provides JSON data about all :class:`.Relation` for a given 
    :class:`.Edge`\.
    
    Parameters
    ----------
    edge_id : int
        An identifier for :class:`.Edge`\.
    
    Returns    
    -------
    HttpResponse
        A Django :class:`HttpResponse` object containing ``application/json``.      
    """

    edge = get_object_or_404(Edge, pk=edge_id)
    return json_response(relation_data(edge.relations.all()))
    