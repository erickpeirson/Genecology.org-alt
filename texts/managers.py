from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from repositories.managers import RepositoryManager
from concepts.managers import retrieve_concept
from texts.models import Text
from django.core.cache import cache
from urlparse import urlparse
import urllib2
import xml.etree.ElementTree as ET
import datetime

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

def list_collections(repo):
    cred = repo.credential
    manager = RepositoryManager(cred)
    collections = cache.get('collections{0}'.format(repo.id))
    if collections is None:
        collections = manager.list_collections()
        cache.set('collections{0}'.format(repo.id), collections, 1000)
    return collections

def list_items(repo, coll):
    cred = repo.credential
    manager = RepositoryManager(cred)
    items = cache.get('items{0}.{1}'.format(repo.id, coll))
    if items is None:
        items = manager.list_items(coll)
        cache.set('items{0}.{1}'.format(repo.id, coll), items, 1000)
    return items

def handle_item(repo, item):
    cred = repo.credential
    manager = RepositoryManager(cred)
    
    # Ignore items without bitstreams.
    if item['primary_bitstream'] in [ None, '-1' ]:
        return None
    
    try:
        text = Text.objects.get(uri=item['uri'])
        exists = True
    except Text.DoesNotExist:
        exists = False
    
    if not exists:
        # Get bitstream.
        bitstream = manager.get_bitstream(item['primary_bitstream'])
        
        # Get Creators.
        creators = []
        for creator in item['creators']:
            creators.append(retrieve_concept(creator))


        text = Text(    uri = item['uri'],
                        title = item['title'],
                        dateCreated = handle_date(item['dateCreated']),
                        dateDigitized = handle_date(item['dateDigitized']),
                        content = bitstream,
                        filename = item['uri'],
                        length = len(bitstream) )
        text.save()
        for creator in creators:
            text.creator.add(creator)
        text.save()
        
        return text
    return None

# TODO: make this not terrible.
def handle_date(date):
    if len(date) == 4:
        return date + '-01-01'
    elif len(date) == 7:
        return date + '-01'
    elif len(date) == 10:
        return date
    return u'1900-01-01'
    
def list_bitstreams(repo, coll, item):
    cred = repo.credential
    manager = RepositoryManager(cred)
    return manager.item_primary_bitstream(item)

