from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from repositories.managers import RepositoryManager
from django.core.cache import cache
from urlparse import urlparse
import urllib2
import xml.etree.ElementTree as ET

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

def list_bitstreams(repo, coll, item):
    cred = repo.credential
    manager = RepositoryManager(cred)
    return manager.item_primary_bitstream(item)
#    return manager.item(item)
