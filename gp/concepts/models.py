from django.db import models
import urllib2

class Concept(models.Model):
    uri = models.CharField(max_length=500, unique=True)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200, blank=True, null=True)
    equalto = models.CharField(max_length=500, blank=True, null=True)
    similarto = models.CharField(max_length=500, blank=True, null=True)
    location = models.ForeignKey('locations.Location', blank=True, null=True)

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
    selected = models.BooleanField(default=False, unique=True)
