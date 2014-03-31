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
        r = re.compile(self.id_pattern)
        m = r.search(path)
        if not m:
            logger.error("Provided path does not conform to LocationAuthority"+\
                         " id_pattern")
            return None
        return m.group(1)

class Location(models.Model):
    name = models.CharField(max_length=200)
    uri = models.CharField(max_length=500, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    class Meta:
        verbose_name_plural = "locations"

class Concept(models.Model):
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
    def get_unique(self, name, uri=None):
        """
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
    e.g. E40 Legal Body
    """
    
    name = models.CharField(max_length='200', unique=True)
    uri = models.CharField(max_length='200', null=True, blank=True, unique=True)

    objects = ConceptTypeManager()

class ConceptAuthority(models.Model):
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