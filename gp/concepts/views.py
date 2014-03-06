from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from concepts.models import Concept, ConceptAuthority
from locations.models import Location

import xml.etree.ElementTree as ET
import urllib2



def retrieve(request, uri):
    try:
        authority = ConceptAuthority.objects.filter(selected=True).get()    
    except ObjectDoesNotExist:
        return HttpResponse("No ConceptAuthority selected.", status=403)
    
    # Check for existing concept before calling the authority.
    try:
        C = Concept.objects.filter(uri=uri).get()
    except ObjectDoesNotExist:
        
        querystring = authority.retrieveformat.format(uri) # "/Concept?id="+uri
        response = urllib2.urlopen(authority.host+querystring).read()
        
        root = ET.fromstring(response)
        data = {}
        if len(root) > 0:
            for node in root:
                if node.tag == '{'+authority.namespace+'}conceptEntry':
                    for snode in node:
                        dkey = snode.tag.replace('{'+authority.namespace+'}', '')
                        data[dkey] = snode.text
                        if snode.tag == '{'+authority.namespace+'}type':
                            data['type_id'] = snode.get('type_id')
                            data['type_uri'] = snode.get('type_uri')
                            
        if data == {}:  # Nothing retrieved
            raise Http404
    
        C = Concept(uri=uri, 
                    name=data['lemma'],
                    type=data['type'],
                    equalto=data['equal_to'],
                    similarto=data['similar_to'])
        C.save()
        
        # Check for geonames URI in similar_to field.
        if data['similar_to'] is not None:
            host = request.get_host()
            loc_uri = urllib2.quote(data['similar_to'])
            loc_id = urllib2.urlopen('http://'+host+'/locations/retrieve/'+loc_uri).read()
            C.location_id = loc_id
            C.save()
                
    return HttpResponse(C.id)
    