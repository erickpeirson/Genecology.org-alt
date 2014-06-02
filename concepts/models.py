"""
Represents conceptual entities, such as people, institutions, organisms, and the 
authorities that describe them.

.. autosummary::

   Location
   LocationAuthority   
   Concept
   ConceptType
   ConceptTypeManager
   ConceptAuthority
   

"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

import urllib2
import re
import simplejson
import xml.etree.ElementTree as ET

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

class LocationAuthority(models.Model):
    """
    A RESTful services that describes :class:`.Location` instances on the earth.
    
    Attributes
    ----------
    name : str
        A human-readable name for this service.
    host : str
        Location (URL) of the REST endpoint.
    namespace : str
        URI prefix for locations belonging to this authority.
    queryformat : str
        A pattern with a :func:`format` replacement element describing how
        to search for a location by name.
    retrieveformat : str
        A pattern with a :func:`format` replacement element describing how
        to retrieve a location by ID. e.g. 
        ``/get?geonameId={0}&username=erickpeirson&style=full``
    id_pattern : str
        A regex pattern that describes how to retrieve IDs from location 
        URIs. e.g. ``http://www.geonames.org/(.*?)/``
    """
    name = models.CharField(max_length=200)
    host = models.CharField(max_length=500)
    # http://api.geonames.org
    namespace = models.CharField(max_length=200, unique=True)
    
    queryformat = models.CharField(max_length=200, blank=True, null=True)
    
    # /get?geonameId={0}0&username=erickpeirson&style=full
    retrieveformat = models.CharField(max_length=200)
    
    # http://www.geonames.org/(.*?)/
    id_pattern = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "location authorities"

    def get_id(self, path):
        """
        Retrieve a location ID from a URI for this authority using 
        ``id_pattern``.
        
        Parameters
        ----------
        path : str
            A location URI for this authority.
        """
        r = re.compile(self.id_pattern)
        m = r.search(path)
        if not m:
            logger.error("Provided path does not conform to LocationAuthority"+\
                         " id_pattern")
            return None
        return m.group(1)

class Location(models.Model):
    """
    Represents a location on the earth.
    
    Attributes
    ----------
    name : str
        A human-readable name.
    uri : str
        URI, presumably in the ``namespace`` of a :class:`.LocationAuthority`\.
    latitude : float
        Decimal degrees North (+) or South (-) of the equator.
    longitude : float
        Decimal degrees West (-) or East (+) for the Prime Meridian.
    """

    name = models.CharField(max_length=200)
    uri = models.CharField(max_length=500, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    class Meta:
        verbose_name_plural = "locations"

    def __unicode__(self):
        return self.name

class Concept(models.Model):
    """
    Represents a unique concept, such as a person or an institution.
    
    Attributes
    ----------
    uri : str
        URI, presumably in the ``namespace`` of a :class:`.ConceptAuthority`\.
    name : str
        A human-readable name.
    type :
        ForeignKey reference to a :class:`.ConceptType`\.
    equalto : str
        (optional) Value of the ``equalto`` relation in Conceptpower.
    similarto : str
        (optional) Value of the ``similarto`` relation in Conceptpower.
    location :
        (optional) ForeignKey reference to a :class:`.Location`\.
    """
            
    uri = models.CharField(max_length=500, unique=True)
    name = models.CharField(max_length=200)
    type = models.ForeignKey('ConceptType')
#    type = models.CharField(max_length=200, blank=True, null=True)
    equalto = models.CharField(max_length=500, blank=True, null=True)
    similarto = models.CharField(max_length=500, blank=True, null=True)
    location = models.ForeignKey('Location', blank=True, null=True)

    class Meta:
        verbose_name_plural = "concepts"

    def __unicode__(self):
        return unicode(self.name)

class ConceptTypeManager(models.Manager):
    """
    Manager for retrieving and creating :class:`.ConceptType`\s.
    
    Instantiated in the ``objects`` attribute of a :class:`.ConceptType`\.
    """
    def get_unique(self, name, uri=None):
        """
        Return or create a :class:`.ConceptType`\.
        
        If ConceptType already exists with that URI, return it. Otherwise create
        a new one.
        """
        try:
            instance = ConceptType.objects.filter(uri=uri).get()
            logger.debug('ConceptType for {0} exists.'.format(uri))
        except ObjectDoesNotExist:
            logger.debug('ConceptType for {0} does not exist. Creating.'
                                                                   .format(uri))
            instance = ConceptType(name=name, uri=uri)
            instance.save()
        return instance

class ConceptType(models.Model):
    """
    An ontological concept for classifying :class:`.Concept`\.
    
    The Genecology Project uses types from the 
    `CIDOC-CRM <http://www.cidoc-crm.org/>`_, e.g. E40 Legal Body.
    
    Attributes
    ----------
    name : str
        A human-readable name.
    uri : str
        URI, presumably in the ``namespace`` of a :class:`.ConceptAuthority`\.
    objects : 
        Instance of :class:`.ConceptTypeManager`\.

    """
    
    name = models.CharField(max_length='200', unique=True)
    uri = models.CharField(max_length='200', null=True, blank=True, unique=True)

    objects = ConceptTypeManager()

    def __unicode__(self):
        return self.name

class ConceptAuthority(models.Model):
    """
    A RESTful services that describes :class:`.Concept` instances.
    
    Attributes
    ----------
    name : str
        A human-readable name for this service.
    host : str
        Location (URL) of the REST endpoint.
    namespace : str
        URI prefix for locations belonging to this authority.
    queryformat : str
        A pattern with a :func:`format` replacement element describing how to search for a concept by name. e.g. ``/ConceptLookup/{0}/{1}`` where ``{0}`` is the query and ``{1}`` is the POS.
    retrieveformat : str
        A pattern with a :func:`format` replacement element describing how to retrieve a concept by ID. e.g. ``/Concept?id={0}``
    """

    host = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    # e.g. "/ConceptLookup/{0}/{1}"
    #  {0} -- query
    #  {1} -- pos
    queryformat = models.CharField(max_length=200)
    
    # e.g. "/Concept?id={0}"
    #  {0} -- uri
    retrieveformat = models.CharField(max_length=200)
    
    # e.g. http//www.digitalhps.org/
    namespace = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "concept authorities"