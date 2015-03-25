from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


import collections
import json
import networkx as nx
from xml.etree import cElementTree as ET

from .models import *
from .writers import GraphMLWriter

def display_text(request, text_id):
    text = get_object_or_404(Text, pk=text_id)
    
    active_node = request.GET.get('node', 'null')
    
    return render( request, 'main/display_text.html', { 'text': text, 'active_node': active_node })

def list_texts(request):
    all_texts = Text.objects.all()
    paginator = Paginator(all_texts, 20)

    page = request.GET.get('page')
    try:
        texts = paginator.page(page)
    except PageNotAnInteger:
        texts = paginator.page(1)
    except EmptyPage:
        texts = paginator.page(paginator.num_pages)

    return render(request, 'main/list_nosidebar.html', { 'texts': texts })


def display_network(request, network_id=1):
    """
    Displays a D3-based network visualization.
    
    User can select shapes representing :class:`.Node` and :class:`.Edge` to get
    more information about their attributes and textual evidence.
    
    Parameters
    ----------
    network_id : int
        (default: 1) Identifier for a :class:`.Network`\.
    """
    return render(request, 'main/network.html',
        {   'network_id': network_id,
            'nav_active': 'network' })

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
    disposition = 'attachment; filename="network_'+network_id+'.graphml'
    response['Content-Disposition'] = disposition
    
    return response

def network_data(network_id):
    """
    Generates data about :class:`.Node` and :class:`.Edge` for a given
    :class:`.Network`\.
    
    Parameters
    ----------
    network_id : int
        Identifier for a :class:`.Network`\.
    
    Returns
    -------
    response_data : dict
        A nested dictionary describing :class:`.Node` and :class:`.Edge`\.
    """
    network = get_object_or_404(Network, pk=network_id)

    # Put it all together.
    response_data = { 'network': {
                        'id': network.id,
                        'name': network.label,
                        'nodes': node_data(network.node_set.all()),
                        'edges': edge_data(network.edge_set.all()),
                        }   }

    return response_data

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
    def _get_uri(obj):
        try: return obj.uri
        except: return 'null'
    
    node_data = [ { 'concept': node.represents.uri,
                    'id': node.id,
                    'type': _get_uri(node.represents.typed),
                    'label': node.label,
                    } for node in nodes ]
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
    edge_data = [ { 'source': edge.source.id,
                    'target': edge.target.id,
                    'id': edge.id,
                    'concept': edge.represents.uri,
                    'label': edge.label,
                    } for edge in edges ]
    return edge_data

def flatten(d, parent_key=''):
    items = []
    for k, v in d.items():
        new_key = parent_key + '_' + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)

