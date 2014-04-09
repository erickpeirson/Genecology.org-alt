"""
managers for Concepts app
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from concepts.models import Concept, ConceptAuthority, ConceptType, \
                            Location, LocationAuthority

from urlparse import urlparse
import urllib2
import xml.etree.ElementTree as ET

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

def retrieve_location(uri):
    """
    If Location for URI already exists, return it. Otherwise, try to resolve
    using LocationAuthority and create/return new Location.
    """

    # Determine namespace.
    # http://www.geonames.org/6946760/penglais-campus-university-of-wales-aberystwyth.html
    namespace = get_namespace(uri)

    # Try to get LocationAuthority by namespace.
    try:
        authority = LocationAuthority.objects.filter(namespace=namespace).get()
    except ObjectDoesNotExist:
        logger.error("No LocationAuthority defined for namespace {0}."
                                                             .format(namespace))
        raise RuntimeError("No LocationAuthority defined for namespace {0}."
                                                             .format(namespace))
    
    # Check to see if Location is already stored locally.
    try:
        location = Location.objects.filter(uri=uri).get()
    except ObjectDoesNotExist:
        # Retrieve the Location from the LocationAuthority.
        location = _remote_location(uri, authority)

    return location

def retrieve_concept(uri):
    """
    If Concept for URI already exists, return it. Otherwise, try to resolve
    using ConceptAuthority and create/return new Concept.
    """
    
    # Determine namespace and find matching ConceptAuthority.
    namespace = get_namespace(uri)
    try:
        authority = ConceptAuthority.objects.filter(namespace=namespace).get()
    except ObjectDoesNotExist:
        logging.error("No ConceptAuthority for namespace {0}.".format(namespace))
        raise RuntimeError("No ConceptAuthority for namespace {0}.".format(namespace))
    
    # Check for existing concept before calling the authority.
    try:
        concept = Concept.objects.filter(uri=uri).get()
        logging.debug("Concept already exists.")
    except ObjectDoesNotExist:
        logging.debug("Concept does not exist.")
        concept = _remote_concept(uri, authority)

    return concept

def get_namespace(uri):
    """
    Extract namespace from URI.
    """
    o = urlparse(uri)
    namespace = o.scheme + "://" + o.netloc
    
    if o.scheme == '' or o.netloc == '':
        logging.error("Could not determine namespace for {0}.".format(uri))
        raise ValueError("Could not determine namespace for {0}.".format(uri))    
    
    return namespace

def _remote_concept(uri, authority):
    """
    Retrieve a Concept from a remote authority service.
    """

    logging.debug("Retrieve remote concept for {0}.".format(uri))
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
        logging.warning("No such concept in ConceptAuthority for "            +\
                        " namespace {0}".format(authority.namespace))
        raise ValueError("No such concept in ConceptAuthority for "           +\
                        " namespace {0}".format(authority.namespace))
    # Get Concept type.
    ctype = ConceptType.objects.get_unique(data['type'], data['type_uri'])

    concept = Concept(uri=uri,
                name=data['lemma'],
                type=ctype,
                equalto=data['equal_to'],
                similarto=data['similar_to'])
    concept.save()
    logging.debug("Concept saved.")

    # Check for geonames URI in similar_to field, and get the corresponding
    #  Location.
    if data['similar_to'] is not None:
        logging.debug("similar_to field is not empty.")
        try:
            location = retrieve_location(data['similar_to'])
        except RuntimeError:
            location = None
        if location is not None:
            logging.debug("Found a Location based on similar_to field")
            concept.location_id = location.id
            concept.save()
        else:
            logging.debug("No Location found.")
    
    return concept

def _remote_location(uri, authority):
    """
    Retrieve a Location from a remote authority service.
    """
        
    logging.debug("Retrieve remote location for {0}.".format(uri))
    id = authority.get_id(uri)
    if id is None:   # Couldn't find an id in the URI.
        logger.warning("Malformed Location URI.")
        raise ValueError("Malformed Location URI.")
    
    querystring = authority.retrieveformat.format(id)
    response = urllib2.urlopen(authority.host + querystring).read()

    tree = ET.fromstring(response)
    if len(tree) <= 1:  # No such Location URI at that Authority.
        logger.warning("No such Location URI at that Authority.")
        return None
    
    lat = tree.findall('.//lat')[0].text
    lng = tree.findall('.//lng')[0].text
    name = tree.findall('.//name')[0].text

    location = Location(uri=uri,
                        name=name,
                        latitude=lat,
                        longitude=lng)
    location.save()
    
    return location
