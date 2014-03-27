from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404

from texts.models import Text

def index(request):
    return HttpResponse("Yup");
    
def geographic(request):
    return render(request, 'browser/geographic.html')

def list_texts(request):
    """
    Lists all Texts
    """
    
    texts = Text.objects.all()
    
    data = {    'title': 'Texts',
                'headers': [ 'Title', 'Length', 'Created', 'Added' ],
                'items': [ [ 
                            { 'link': '/browser/texts/{0}'.format(text.id),
                              'text': text.title }, 
                            { 'text': text.length },
                            { 'text': text.dateCreated }, 
                            { 'text': text.dateAdded } ] for text in texts ] }
    
    return render_to_response('browser/list_nosidebar.html', data)

def display_text(request, text_id):
    """
    Displays a text.
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
                            { 'link': '/browser/texts/{0}'.format(text.id),
                              'text': text.title }, 
                            { 'text': text.dateCreated } ] for text in texts ] }

            
    data = {    'title': text.title,
                'subtitle': text.uri,
                'text': text.content,
                'leftlist': tdata }
    return render_to_response('browser/base_leftsidebar.html', data)
                