"""
Provides a dynamic HTML inferface for end users.

.. autosummary::

   index
   list_texts
   display_text
   display_network
   data
   participate
   geographic
"""

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404
from browser.managers import text_appellations, text_relations, \
                             add_appellations

from texts.models import Text

def index(request):
    """
    Front page of the GP website.
    """
    return render_to_response('browser/base_home.html', {'nav_active': 'home'})
    
def geographic(request):
    """
    OLD: Renders a geocoded network.
    """
    return render(request, 'browser/geographic.html')

def list_texts(request):
    """
    Lists all :class:`.Text` in the database. User can click to view text and
    associated network data.
    """
    
    texts = Text.objects.all()
    
    data = {    'title': 'Texts',
                'headers': [ 'Title', 'Date', 'Nodes', 'Edges' ],
                'items': [ [ 
                            { 'link': '/browser/texts/{0}/'.format(text.id),
                              'text': text.title }, 
                            { 'text': text.dateCreated.year },
                            { 'text': len(text_appellations(text)) }, 
                            { 'text': len(text_relations(text)) } 
                        ] for text in texts ],
                'nav_active': 'texts' }
    
    return render_to_response('browser/list_nosidebar.html', data)

def display_text(request, text_id):
    """
    Displays a :class:`.Text`, along with associated network data.
    
    Appellations are highlighted in-text, and the user can navigate network
    data by clicking nodes or highlighted appellations.
    
    Parameters
    ----------
    text_id : int
        Identifier for a :class:`.Text`\.
    """
    
    try:
        text = Text.objects.get(pk=text_id)
    except Text.DoesNotExist:
        try:
            text = Text.objects.get(uri=text_id)
        except Text.DoesNotExist:
            raise Http404

    texts = Text.objects.all()
    
    tdata = {   'title': 'Texts',
                'footer': {
                    'text': 'List all texts...',
                    'link': '/browser/texts/'
                },
                'items': [ [ 
                            { 'link': '/browser/texts/{0}/'.format(t.id),
                              'text': t.title }, 
                            { 'text': t.dateCreated } ] for t in texts ] }


    content = add_appellations(text, snip=text.restricted)



    data = {    'title': text.title,
                'text_id': text.id,
                'uri': text.uri,
                'text': content,
                'leftlist': tdata,
                'nav_active': 'texts' }

    return render_to_response('browser/display_text.html', data)

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
    return render_to_response('browser/network.html', {'network_id': network_id,
                                                        'nav_active': 'network'})


def data(request):
    """
    Describes how users can access and use Genecology Project data for their own
    research.
    """
    data = {'nav_active': 'data',
            'paragraphs': [
                { 'text': 'This page describes how you can access and use'    +\
                          ' our data for your own research.' },
                { 'text': '[ Downloading network datasets ]' },
                { 'text': '[ Connecting to our RESTful API ]' },
                { 'text': '[ Downloading our corpus model ]' },
                { 'text': '' } ] }
                          
    return render_to_response('browser/base_nosidebar.html', data)

def participate(request):
    """
    Describes how users can contribute to the Genecology Project.
    """
    data = {'nav_active': 'participate',
            'paragraphs': [
                { 'text': 'This page describes how you can contribute to the' +\
                          ' Genecology Project.' },
                { 'text': '[ Annotated texts ]' },
                { 'text': '[ Archival materials ]' },
                { 'text': '[ Oral histories ]' },
                { 'text': '[ Comments & suggestions ]' },
                { 'text': '' } ] }
                          
    return render_to_response('browser/base_nosidebar.html', data)
