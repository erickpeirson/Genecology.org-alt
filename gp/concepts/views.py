from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.core.urlresolvers import reverse

from django.core import serializers
import simplejson

from concepts.managers import retrieve_location
from concepts.models import Concept, ConceptAuthority, \
                            Location, LocationAuthority

import xml.etree.ElementTree as ET
import urllib2

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

def retrieve(request, uri):
    try:
        authority = ConceptAuthority.objects.filter(selected=True).get()    
    except ObjectDoesNotExist:
        return HttpResponse("No ConceptAuthority selected.", status=403)
    
    # Check for existing concept before calling the authority.
    try:
        C = Concept.objects.filter(uri=uri).get()
        logging.debug("Concept already exists.")
    except ObjectDoesNotExist:
        logging.debug("Concept does not exist.")
        querystring = authority.retrieveformat.format(uri)  # "/Concept?id="+uri
        response = urllib2.urlopen(authority.host+querystring).read()

        root = ET.fromstring(response)
        data = {}
        if len(root) > 0:
            for node in root:
                if node.tag == '{'+authority.namespace+'/}conceptEntry':
                    for sn in node:
                        dkey = sn.tag.replace('{'+authority.namespace+'/}','')
                        data[dkey] = sn.text
                        if sn.tag == '{'+authority.namespace+'/}type':
                            data['type_id'] = sn.get('type_id')
                            data['type_uri'] = sn.get('type_uri')

        if data == {}:  # Nothing retrieved
            logging.warning("No such concept in ConceptAuthority for "        +\
                            " namespace {0}".format(authority.namespace))
            raise Http404

        C = Concept(uri=uri, 
                    name=data['lemma'],
                    type=data['type'],
                    equalto=data['equal_to'],
                    similarto=data['similar_to'])
        C.save()
        logging.debug("Concept saved.")

        # Check for geonames URI in similar_to field, and get the corresponding
        #  Location.
        if data['similar_to'] is not None:
            logging.debug("similar_to field is not empty.")
            location = retrieve_location(data['similar_to'])
            if location is not None:
                logging.debug("Found a Location based on similar_to field")
                C.location_id = location.id
            else:
                logging.debug("No Location found.")

    # Return the Concept as JSON.
    response_data = { 'id': C.id,
                      'uri': C.uri,
                      'type': C.type,
                      'location': C.location_id,
                      'equalto': C.equalto,
                      'similarto': C.similarto }
    
    jdata = simplejson.dumps(response_data)
    return HttpResponse(jdata, "application/json")


