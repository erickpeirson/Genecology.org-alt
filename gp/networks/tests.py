from django.test import TestCase
from models import NodeType

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