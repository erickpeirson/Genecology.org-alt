from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.contrib import messages

from django.core import serializers
import simplejson

from concepts.managers import retrieve_concept
from concepts.models import Concept, ConceptAuthority, \
                            Location, LocationAuthority
from concepts.forms import AddConceptForm

import xml.etree.ElementTree as ET
import urllib2

def retrieve(request, uri):
    try:
        concept = retrieve_concept(uri)
    except RuntimeError:
        return HttpResponse("No ConceptAuthority selected.", status=403)
    except ValueError:
        raise Http404

    # Return the Concept as JSON.
    response_data = { 'id': concept.id,
                      'uri': concept.uri,
                      'type': concept.type,
                      'location': concept.location_id,
                      'equalto': concept.equalto,
                      'similarto': concept.similarto }
    
    jdata = simplejson.dumps(response_data)
    return HttpResponse(jdata, "application/json")
