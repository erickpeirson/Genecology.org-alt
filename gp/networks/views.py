"""
views for Networks app.
"""

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseNotFound
from networks.models import Network, Node, Edge

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
    
    print edges[0].relations.all()
    
    return HttpResponse(str(features) + str(linestrings))


