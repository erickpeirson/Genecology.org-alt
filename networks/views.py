"""
views for Networks app.
"""

from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from networks.models import Network, Node, Edge, Dataset, Appellation, \
                            Relation, NetworkProjection

import simplejson
from pprint import pprint

def index(request):
    return HttpResponse('Woohoo!')

def json_response(response_data):
    response_json = simplejson.dumps(response_data)
    return HttpResponse(response_json, 'application/json')

def appellation_data(appellations):
    app_data = []
    for app in appellations:
        print app.textposition
        ad = { 'concept': app.concept.uri,
               'type': app.concept.type.uri,
               'id': app.id     }
        if app.textposition is not None:
            ad['textposition'] = {
                'text_id': app.textposition.text.id,
                'text_title': app.textposition.text.title,
                'text': app.textposition.text.uri,
                'startposition': app.textposition.startposition,
                'endposition': app.textposition.endposition       
                }
        app_data.append(ad)
    return {'appellations': app_data}

def node_data(nodes):
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
    return [ {  'source': edge.source.id,
                'target': edge.target.id,
                'id': edge.id,
                'concept': edge.concept.uri,
                'label': edge.concept.name,
                'relations': [ r.id for r in edge.relations.all() ]
                } for edge in edges ]

def relation_data(relations):
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

    return {'relations': rel_data}

def dataset_endpoint(request, dataset_id):
    """
    The Dataset Endpoint view provides JSON describing Appellations and 
    Relations for a specified dataset.
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
    
def network_endpoint(request, network_id):
    """
    The Network Endpoint view provides JSON describing Nodes and Edges for a 
    specified Network.
    """
    network = get_object_or_404(Network, pk=network_id)
    
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
    
    # And we're done.
    return json_response(response_data)

def network_projection(request, network_id, projection_id):
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

    network = get_object_or_404(Network, pk=network_id)
    projection = get_object_or_404(NetworkProjection, pk=projection_id)
    node_types = [ p.primaryNode for p in projection.mappings.all() ]

    # Generate node mappings based on projection.
    edges = network.edges.all()
    node_mappings = {}
    for e in edges:
        map = project_edge(e, projection)
        if map is not None:
            try:
                node_mappings[map['secondary'].id] += map['node'].id
            except (KeyError, TypeError):
                node_mappings[map['secondary'].id] = [map['node'].id]

    # Generate a new edge list based on node mappings.
    c_nodes = {}
    c_edges = []
    node_index = {}
    include_nodes = set([])
    for e in edges:
        collapsed = None
        try:
            source = node_mappings[e.source.id][0]
            collapsed = 'source'
            
            # Update primary node.
            try:
                c_nodes[e.target.id]['contains'] += [source]
            except KeyError:
                c_nodes[e.target.id] = { 'contains': [source] }
        except KeyError:    # No mapping defined for source node.
            source = e.source.id

        try:
            target = node_mappings[e.target.id][0]
            collapsed = 'target'
            
            # Update primary node.
            try:
                c_nodes[e.source.id]['contains'] += [target]
            except KeyError:
                c_nodes[e.source.id] = { 'contains': [target] }
        except KeyError:    # No mapping defined for target node.
            target = e.target.id

        source_node = Node.objects.get(pk=source)
        target_node = Node.objects.get(pk=target)
        node_index[source] = source_node
        node_index[target] = target_node

        # Only include edges between primaryNodes in the Projection.
        # TODO: Handle case where source or target has no location.
        if source_node.type in node_types\
                            and target_node.type in node_types:
            new_edge = {    'source': source,
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
                            }
                        }
            c_edges.append(new_edge)
            
            if collapsed is not None:
                new_edge['original'] = e.id
            
            include_nodes.add(source)
            include_nodes.add(target)
    
    # TODO: Can this be done with data already retrieved?
    all_nodes = [ node_index[id] for id in include_nodes ]

    return json_response({'network': {'edges': c_edges, 'nodes': node_data(all_nodes) }})

def list_datasets(request):
    """
    Returns a list of datasets (JSON).
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
    Returns a list of networks (JSON).
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
    Returns all appellations (for a text, if text_id is provided).
    """

    appellations = Appellation.objects.all()
    relations = Relation.objects.all()
    
    if text_id is not None:
        appellations = appellations.filter(textposition__text__id=text_id)
        relations = relations.filter(predicate__textposition__text__id=text_id)
    
    # Build appellation response.
    return json_response(dict(appellation_data(appellations).items() + relation_data(relations).items()))

def text_network(request, text_id=None, network_id=None):
    """
    Returns network data (nodes, edges, appellations, relations) rooted in a 
    text.
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
    Returns all appellations for a node.
    """
    node = get_object_or_404(Node, pk=node_id)
    return json_response(appellation_data(node.appellations.all()))

def edge_relations(request, edge_id):
    """
    Returns all relations for an edge.
    """

    edge = get_object_or_404(Edge, pk=edge_id)
    return json_response(relation_data(edge.relations.all()))