"""
views for Networks app.
"""

from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from networks.models import Network, Node, Edge, Dataset

import simplejson

def index(request):
    return HttpResponse('Woohoo!')

def get_network(request, network_id):
    """
    should return some JSON with nodes (Features) and edges (LineStrings)
    """

    network = Network.objects.get(pk=network_id)

    nodes = [ n for n in network.nodes.all() ]
    edges = [ e for e in network.edges.all() ]

    features = [ {  'id': n.id,
                    'label': n.concept.name } for n in nodes ]
    
    linestrings = [ {   'id': e.id,
                        'source': e.source.id,
                        'target': e.target.id,
                        'label': e.concept.name,
                        'predicate': e.concept.id,
                        'strength': len(e.relations.all()) } for e in edges ]
    
    return HttpResponse(str(features) + str(linestrings))

def dataset_endpoint(request, dataset_id):
    """
    The Dataset Endpoint view provides JSON describing Appellations and 
    Relations for a specified dataset.
    """

    dataset = get_object_or_404(Dataset, pk=dataset_id)
    
    # Build appellation response.
    app_data = []
    for app in dataset.appellations.all():
        ad = { 'concept': app.concept.uri,
               'id': app.id     }
        if app.textposition is not None:
            ad['textposition'] = { 
                'text': app.textposition.text.uri,
                'startposition': app.textposition.startposition,
                'endposition': app.textposition.endposition       
                }
        app_data.append(ad)
    
    # Build relation response.
    rel_data = [  { 'source': rel.source.id,
                    'target': rel.target.id,
                    'predicate': rel.predicate.id } for rel 
                                                    in dataset.relations.all() ]

    # Put it all together.
    response_data = { 'dataset': { 
                        'id': dataset.id,
                        'name': dataset.name,
                        'added': str(dataset.added),
                        'networks': [n.id for n in dataset.networks.all()],
                        'appellations': app_data,
                        'relations': rel_data }}

    # And we're done.
    response_json = simplejson.dumps(response_data)
    return HttpResponse(response_json, 'application/json')
    
def network_endpoint(request, network_id):
    """
    The Network Endpoint view provides JSON describing Nodes and Edges for a 
    specified Network.
    """
    network = get_object_or_404(Network, pk=network_id)
    
    # Build node response.
    node_data = [ { 'concept': node.concept.uri,
                    'id': node.id,
                    'type': node.type.uri,
                    'label': node.concept.name,
                    'appellations': [ a.id for a in node.appellations.all() ]
                } for node in network.nodes.all() ]
    
    # Build edge response.
    edge_data = [ { 'source': edge.source.id,
                    'target': edge.target.id,
                    'id': edge.id,
                    'concept': edge.concept.uri,
                    'label': edge.concept.name,
                    'relations': [ r.id for r in edge.relations.all() ]
                } for edge in network.edges.all() ]

    # Put it all together.
    response_data = { 'network': {
                        'id': network.id,
                        'name': network.name,
                        'nodes': node_data,
                        'edges': edge_data  }}
    
    # And we're done.
    response_json = simplejson.dumps(response_data)
    return HttpResponse(response_json, 'application/json')