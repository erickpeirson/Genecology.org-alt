from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from text.models import Text, Repository

from urlparse import urlparse
import urllib2
import xml.etree.ElementTree as ET

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

def retrieve_text(repository, text):
    