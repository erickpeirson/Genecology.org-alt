from django.db import models
import re

class LocationAuthority(models.Model):
    name = models.CharField(max_length=200)
    host = models.CharField(max_length=500)
    namespace = models.CharField(max_length=200, unique=True)
    
    queryformat = models.CharField(max_length=200, blank=True, null=True)
    
    retrieveformat = models.CharField(max_length=200)
    
    def get_id(self, path):
        r = re.compile('http://www.geonames.org/(.*?)/')
        m = r.search(path)
        if not m:
            return None
        return m.group(1)

class Location(models.Model):
    name = models.CharField(max_length=200)
    uri = models.CharField(max_length=500, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
