from django.test import TestCase
from django.test.client import RequestFactory
from django.http import HttpResponse, HttpRequest, Http404
from django.db import IntegrityError

import simplejson
from concepts.managers import retrieve_location, retrieve_concept, \
                              get_concept_type

from concepts.models import Concept, ConceptAuthority, \
                            Location, LocationAuthority
from concepts.views import retrieve

import logging
logging.disable(logging.CRITICAL)

cp_concept = 'http://www.digitalhps.org/concepts/CON397335ef-1870-46ff-82ff-346328dc6375'
gn_uri = 'http://www.geonames.org/6946760/penglais-campus-university-of-wales-aberystwyth.html'

def create_concept_authority():
    concept_authority = ConceptAuthority(
        host='http://chps.asu.edu/conceptpower/rest',
        name='ASU Conceptpower',
        queryformat='/ConceptLookup/{0}/{1}',
        retrieveformat='/Concept?id={0}',
        namespace='http://www.digitalhps.org')
        
    concept_authority.save()
    return concept_authority

def create_location_authority():
    location_authority = LocationAuthority(
        name='Geonames',
        namespace='http://www.geonames.org',
        host='http://api.geonames.org',
        retrieveformat='/get?geonameId={0}&username=erickpeirson&style=full',
        id_pattern='http://www.geonames.org/(.*?)/' )
    location_authority.save()
    return location_authority

class RetrieveLocationGeonamesTests(TestCase):
    """
    tests for concepts.managers.retrieve_location
    """

    def setUp(self):
        create_location_authority()

    def test_retrieve_location(self):
        """
        If provided a legit geonames URI, should return a Location object with
        that URI.
        """
        location = retrieve_location(gn_uri)
        self.assertEqual(location.uri, gn_uri)

    def test_retrieve_location_again(self):
        """
        If provided a geonames URI that has already been retrieved, should
        return a Location object with that URI.
        """
        location = retrieve_location(gn_uri)
        self.assertEqual(location.uri, gn_uri)

    def test_retrieve_badns(self):
        """
        If the URI is from a namespace for which no LocationAuthority is defined
        should raise a RuntimeError.
        """
        badns_uri = "http://nonsense.com/abc123"
        self.assertRaises(RuntimeError, retrieve_location, badns_uri)

    def test_retrieve_nonsense(self):
        """
        If the URI namespace is OK, but the URI is malformed (i.e. ID not where
        expected, given LocationAuthority's id_pattern), should raise a
        ValueError.
        """
        badid_uri = 'http://www.geonames.org/foul6946760'
        self.assertRaises(ValueError, retrieve_location, badid_uri)

    def test_retrieve_nonexistent(self):
        """
        If the URI simply does not exist at that LocationAuthority, should
        return None.
        """
        nonexistent_uri = 'http://www.geonames.org/6943991012349326760/asdf'
        location = retrieve_location(nonexistent_uri)
        self.assertEqual(location, None)

class ConceptsRetrieveTests(TestCase):
    """
    tests for concepts.managers.retrieve_concept
    """
    def setUp(self):
        create_concept_authority()
        create_location_authority()

    def test_retrieve_legit_concept(self):
        """
        If a legit concept from the ConceptAuthority is provided, then should
        get a Concept object with uri = provided uri.
        """

        concept = retrieve_concept(cp_concept)
        self.assertIsInstance(concept, Concept)
        self.assertEqual(concept.uri, cp_concept)

    def test_retrieve_nonsense_concept(self):
        """
        If the concept doesn't exist in the ConceptAuthority, should raise
        a ValueError.
        """

        self.assertRaises(ValueError, retrieve_concept, cp_concept+'asdf')
    
    def test_retrieve_nonamespace(self):
        """
        If retrieve_concept can't determine the namespace of the concept, then
        should raise a ValueError.
        """
    
        self.assertRaises(ValueError, retrieve_concept, 'wtfbbqlolrofl')

    def test_retrieve_without_conceptauthority(self):
        """
        If a ConceptAuthority does not exist, or is not selected, should raise
        a RuntimeError.
        """

        ConceptAuthority.objects.get().delete()
        self.assertRaises(RuntimeError, retrieve_concept, cp_concept)

class ConceptsViewRetrieveTests(TestCase):
    """
    tests for concepts.views.retrieve at /concepts/retrieve/
    """

    def setUp(self):
        self.factory = RequestFactory()
        create_concept_authority()
        create_location_authority()
        self.request = self.factory.get('/concepts/retrieve/')
        
    def test_retrieve_legit_concept(self):
        """
        If a legit concept from the ConceptAuthority is provided, then should
        get status 200 and some json.
        """
        
        response = retrieve(self.request, cp_concept)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(simplejson.loads(response.content)['uri'], cp_concept)

    def test_retrieve_nonsense_concept(self):
        """
        If the concept doesn't exist in the ConceptAuthority, should get status
        404.
        """

        self.assertRaises(Http404, retrieve, self.request, cp_concept+'asdf')

    def test_retrieve_nonamespace(self):
        """
        If retrieve_concept can't determine the namespace of the concept, then
        should return 404.
        """
        
        self.assertRaises(Http404, retrieve, self.request, 'wtfbbqlolrofl')

    def test_retrieve_without_conceptauthority(self):
        """
        If a ConceptAuthority does not exist, or is not selected, should 
        return status code 403.
        """

        ConceptAuthority.objects.get().delete()
        response = retrieve(self.request, cp_concept)
        self.assertEqual(response.status_code, 403)

class LocationAuthorityTests(TestCase):
    """
    tests concepts.models.LocationAuthority
    """
    def test_namespace_unique(self):
        """
        the namespace column must be unique
        """
        la = LocationAuthority( name='testAuthority',
                                host='testHost',
                                namespace='testNamespace',
                                retrieveformat='testFormat',
                                id_pattern='testPattern')
        la.save()
        la2 = LocationAuthority( name='testAuthority',
                                host='testHost',
                                namespace='testNamespace',
                                retrieveformat='testFormat',
                                id_pattern='testPattern')
        self.assertRaises(IntegrityError, la2.save)

    def test_get_id_legit(self):
        """
        tests concepts.models.LocationAuthority.get_id. If provided path
        conforms to the LocationAuthority.id_pattern, then should return a
        string id.
        """
        
        location_authority = create_location_authority()
        expected_id = "6946760"
        observed_id = location_authority.get_id(gn_uri)
        self.assertEqual(observed_id, expected_id)

    def test_get_id_badformat(self):
        """
        tests concepts.models.LocationAuthority.get_id. If provided path does
        not conform to the LocationAuthority.id_pattern, then should return
        None.
        """
        location_authority = create_location_authority()
        nonsense_path = "lolwtfbbq42"
        observed_id = location_authority.get_id(nonsense_path)
        self.assertEqual(observed_id, None)

class ConceptAuthorityTests(TestCase):
    """
    tests concepts.models.ConceptAuthority
    """

    def test_namespace_unique(self):
        """
        the namespace column must be unique
        """
        ca = ConceptAuthority(
            host='http://chps.asu.edu/conceptpower/rest',
            name='ASU Conceptpower',
            queryformat='/ConceptLookup/{0}/{1}',
            retrieveformat='/Concept?id={0}',
            namespace='http://www.digitalhps.org')
        ca.save()
        ca2 = ConceptAuthority(
            host='http://chps.asu.edu/conceptpower/rest',
            name='ASU Conceptpower',
            queryformat='/ConceptLookup/{0}/{1}',
            retrieveformat='/Concept?id={0}',
            namespace='http://www.digitalhps.org')
        
        self.assertRaises(IntegrityError, ca2.save)

class GetConceptTypeTests(TestCase):
    """
    """
    
    def setUp(self):
        create_concept_authority()
        create_location_authority()
    
    
        
