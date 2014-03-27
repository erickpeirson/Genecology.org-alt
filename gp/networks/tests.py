import datetime
import simplejson
from pprint import pprint

from django.test import TestCase, RequestFactory
from django.http import Http404

from models import NodeType

from concepts.models import Concept, ConceptAuthority, ConceptType, \
                            Location, LocationAuthority
from concepts.managers import retrieve_concept

from networks.models import Node, NodeType, Appellation, Relation, Dataset, \
                            Network, Edge, NetworkLink, TextPosition

from networks.views import dataset_endpoint, network_endpoint

from texts.models import Text

from networks.managers import DatasetManager

cp_concept = 'http://www.digitalhps.org/concepts/CON397335ef-1870-46ff-82ff-346328dc6375'
cp_concept_type_uri = 'http://www.digitalhps.org/types/TYPE_3fc436d0-26e7-472c-94de-0b712b66b3f3'
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

def create_text():
    textpath = './networks/testdata/testtext1.txt'
    text = Text(uri='http://test/testtext1',
                filename='testtext1.txt',
                title='The Test Text',
                dateCreated = datetime.date(2003,05,01),
                dateDigitized = datetime.date(2005, 02, 03),
                content = open(textpath, 'rb').read())
    text.save()
    return text
    
def create_dataset(network):
    dataset = Dataset(name='TestDataset')
    dataset.save()
    return dataset

def create_network():
    network = Network(name='TestNetwork')
    network.save()
    return network

class NodeTypeTests(TestCase):
    def setUp(self):
        self.testname = 'testname'
        self.testuri = 'testuri'

    def test_node_type_get_unique(self):
        """
        on first call, get_unique should return a NodeType (that it creates).
        """

        ntype = NodeType.objects.get_unique(self.testname, self.testuri)
        self.assertIsInstance(ntype, NodeType)

    def test_node_type_get_unique_second(self):
        """
        on the second call with same args, should return a NodeType, but not
        create a new one
        """

        ntype_ = NodeType.objects.get_unique(self.testname, self.testuri)
        ntype = NodeType.objects.get_unique(self.testname, self.testuri)
        self.assertIsInstance(ntype, NodeType)
        self.assertEqual(len(NodeType.objects.all()), 1)

    def test_node_type_uri_none(self):
        """
        passing no uri should set NodeType.uri == None; and be treated uniquely.
        """

        ntype_ = NodeType.objects.get_unique(self.testname)
        ntype = NodeType.objects.get_unique(self.testname)
        self.assertIsInstance(ntype, NodeType)
        self.assertEqual(ntype.uri, None)
        self.assertEqual(len(NodeType.objects.all()), 1)

class NodeTests(TestCase):
    def setUp(self):
        create_location_authority()
        create_concept_authority()
    
        self.concept = retrieve_concept(cp_concept)
        self.node = Node(concept=self.concept)
        self.node.save()

    def test_node_save_adds_nodetype(self):
        """
        When a node is saved for the first time, a NodeType should be
        automatically created/linked based on the Node's concept.
        """

        self.assertIsInstance(self.node.type, NodeType)
        self.assertEqual(self.node.type.uri, self.concept.type.uri)

class NodeTestGetUnique(TestCase):
    def setUp(self):
        create_location_authority()
        create_concept_authority()

        self.concept = retrieve_concept(cp_concept)
        self.firstNode = Node.objects.get_unique(self.concept)
        self.secondNode = Node.objects.get_unique(self.concept)

    def test_first_get_unique(self):
        """
        Should return a Node with .concept.uri == self.concept.uri,
        and .type.uri == self.concept.type.uri
        """
        self.assertIsInstance(self.firstNode, Node)
        self.assertEqual(self.firstNode.concept.uri, self.concept.uri)
        self.assertEqual(self.firstNode.type.uri, self.concept.type.uri)

    def test_second_get_unique(self):
        self.assertIsInstance(self.secondNode, Node)
        self.assertEqual(len(Node.objects.all()), 1)

class DatasetManagerTests(TestCase):
    def setUp(self):
        create_concept_authority()
        create_location_authority()

        self.network = create_network()
        self.dataset = create_dataset(self.network)

        self.manager = DatasetManager(self.dataset)
        
        # Mimick form data.
        datapath = './networks/testdata/testnetwork.xgmml'
        self.cleaned_data = { 'format': 'XGMML',
                              'upload': open(datapath, 'rb') }
        self.formdata = { 'linked_dataset-0-network': self.network.id }
    
        # Mimick data from parsed dataset.
        self.app_datum = { 'id': cp_concept }
        
        self.text_uri = 'http://test/testtext1'
        self.startpos = 5
        self.endpos = 10
        
        self.app_datum_text = { 'id': cp_concept,
                                'attributes': { 'text': self.text_uri,
                                                'startposition': self.startpos,
                                                'endposition': self.endpos } }                                                
        self.rel_datum = { 'source': cp_concept,
                           'target': cp_concept,
                           'attributes': { 'predicate': cp_concept } }
                           
        self.rel_datum_text = { 'source': cp_concept,
                                'target': cp_concept,
                                'attributes': { 'predicate': cp_concept,
                                                'text': self.text_uri,
                                                'startposition': self.startpos,
                                                'endposition': self.endpos } }

    def test_add_appellation(self):
        """
        tests for DatasetManager._add_appellation()
        """
        
        appellation = self.manager._add_appellation(self.app_datum,
                                                    self.network)

        # Returns an Appellation?
        self.assertIsInstance(appellation, Appellation)
        
        # Concept.uri same as provided?
        self.assertEqual(appellation.concept.uri, cp_concept)

        # Create a new Node?
        self.assertEqual(len(Node.objects.all()), 1)

        # Node has correct Concept?
        node = Node.objects.get()
        self.assertEqual(node.concept.uri, appellation.concept.uri)
        
        # Node references Appellation?
        self.assertIn(appellation, node.appellations.all())

        # Node is in Network?
        self.assertIn(node, self.network.nodes.all())
    
    def test_add_appellation_text_position(self):
        """
        tests for DatasetManager._add_appellation(), where text, startposition,
        and endposition are provided.
        """    
        # If text does not exist, create appellation without it.
        appellation = self.manager._add_appellation(self.app_datum_text,
                                                    self.network)
        self.assertIsInstance(appellation, Appellation)
        
        # If text exists, create a TextPosition.        
        create_text()
        appellation = self.manager._add_appellation(self.app_datum_text,
                                                    self.network)
        self.assertIsInstance(appellation.textposition, TextPosition)
        
        # TextPosition should have correct Text URI, start and end positions.
        self.assertEqual(appellation.textposition.text.uri, self.text_uri)
        self.assertEqual(appellation.textposition.startposition, self.startpos)
        self.assertEqual(appellation.textposition.endposition, self.endpos)


    def test_add_relation(self):
        """
        tests for DatasetManager._add_relation()
        """
        relation = self.manager._add_relation(self.rel_datum, self.network)

        # Returns a Relation?
        self.assertIsInstance(relation, Relation)

        # Predicate Appellation Concept is as provided?
        self.assertEqual(relation.predicate.concept.uri, cp_concept)

        # Source and Target as provided?
        self.assertEqual(relation.source.concept.uri, cp_concept)
        self.assertEqual(relation.target.concept.uri, cp_concept)

        # Creates an Edge?
        edge = Edge.objects.get()
        self.assertEqual(edge.concept.uri, cp_concept)
        
        # Edge references Relation?
        self.assertIn(relation, edge.relations.all())

        # Edge is in Network?
        self.assertIn(edge, self.network.edges.all())

    def test_add_relation_text(self):
        """
        tests for DatasetManager._add_relation(), where text, startposition,
        and endposition are provided.
        """        
        # If text does not exist, create appellation without it.
        relation = self.manager._add_relation(self.rel_datum_text,
                                              self.network)
        self.assertIsInstance(relation.predicate, Appellation)
        
        # If text exists, create a TextPosition.        
        create_text()
        relation = self.manager._add_relation(self.rel_datum_text,
                                              self.network)
        self.assertIsInstance(relation.predicate.textposition, TextPosition)
        
        # TextPosition should have correct Text URI, start and end positions.
        self.assertEqual(relation.predicate.textposition.text.uri, 
                         self.text_uri)
        self.assertEqual(relation.predicate.textposition.startposition, 
                         self.startpos)
        self.assertEqual(relation.predicate.textposition.endposition, 
                         self.endpos)        

    def test_add_dataset(self):
        """
        tests for DatasetManager.add_dataset()
        """

        create_text()
        dataset = self.manager.add_dataset(self.cleaned_data, self.formdata)
        
        # Dataset has 7 appellations (4 nodes + 3 edges).
        appellations = dataset.appellations.all()
        self.assertEqual(len(appellations), 7)
        
        # Dataset Appellations have TextPositions
        self.assertIsInstance(appellations[0].textposition, TextPosition)

        # Dataset has 3 relations.
        relations = dataset.relations.all()
        self.assertEqual(len(relations), 3)

        # Dataset has 1 network, with pk==1.
        networks = dataset.networks.all()
        self.assertEqual(len(networks), 1)
        self.assertEqual(networks[0].id, self.network.id)

class DatasetEndpointView(TestCase):
    """
    The Dataset Endpoint view provides JSON describing Appellations and 
    Relations for a specified dataset.
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        
        create_concept_authority()
        create_location_authority()
        self.text = create_text()

        self.network = create_network()
        self.dataset = create_dataset(self.network)

        self.manager = DatasetManager(self.dataset)
        
        # Mimick form data.
        datapath = './networks/testdata/testnetwork.xgmml'
        self.cleaned_data = { 'format': 'XGMML',
                              'upload': open(datapath, 'rb') }
        self.formdata = { 'linked_dataset-0-network': self.network.id }
        
        self.dataset = self.manager.add_dataset(self.cleaned_data,
                                                self.formdata)

    def test_nonexistent_dataset(self):
        """
        should raise a 404 if dataset with specified id doesn't exist
        """
        request = self.factory.get('/networks/dataset/')
        self.assertRaises(Http404, dataset_endpoint, request, 2)
        
    def test_dataset_exists(self):
        """
        should return status 200 if dataset does exist.
        """
        request = self.factory.get('/networks/dataset/')
        response = dataset_endpoint(request, self.dataset.id)
        self.assertEqual(response.status_code, 200)
    
    def test_returns_json(self):
        request = self.factory.get('/networks/dataset/')
        response = dataset_endpoint(request, self.dataset.id)
        content_type = response._headers['content-type'][1]
        self.assertEqual(content_type, 'application/json')
        
        # Dataset id is correct?
        rdata = simplejson.loads(response.content)
        self.assertEqual(rdata['dataset']['id'], self.dataset.id)

        # Appellations provided?
        self.assertIn('appellations', rdata['dataset'])
        
        # Relations provided?
        self.assertIn('relations', rdata['dataset'])
        
class NetworkEndpointView(TestCase):
    """
    The Network Endpoint view provides JSON describing Nodes and Edges for a 
    specified Network.
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        
        create_concept_authority()
        create_location_authority()
        self.text = create_text()

        self.network = create_network()
        self.dataset = create_dataset(self.network)

        self.manager = DatasetManager(self.dataset)
        
        # Mimick form data.
        datapath = './networks/testdata/testnetwork.xgmml'
        self.cleaned_data = { 'format': 'XGMML',
                              'upload': open(datapath, 'rb') }
        self.formdata = { 'linked_dataset-0-network': self.network.id }
        
        self.dataset = self.manager.add_dataset(self.cleaned_data,
                                                self.formdata)

    def test_nonexistent_network(self):
        """
        should raise a 404 if network with specified id doesn't exist
        """
        request = self.factory.get('/networks/network/')
        self.assertRaises(Http404, network_endpoint, request, 2)
    
    def test_network_exists(self):
        """
        should return 200 if network does exist.
        """
        
        request = self.factory.get('/networks/network/')
        response = network_endpoint(request, self.network.id)
        self.assertEqual(response.status_code, 200)

    def test_returns_json(self):
        request = self.factory.get('/networks/network/')
        response = network_endpoint(request, self.network.id)
        content_type = response._headers['content-type'][1]
        self.assertEqual(content_type, 'application/json')
        
        # Network id is correct?
        rdata = simplejson.loads(response.content)
        self.assertEqual(rdata['network']['id'], self.network.id)

        # Nodes provided?
        self.assertIn('nodes', rdata['network'])
        
        # Edges provided?
        self.assertIn('edges', rdata['network'])
                