from django.test import TestCase
from main.processors import *
from main import authorities

class ProcessVogonXGMMLCase(TestCase):
    def setUp(self):
        with open('/Users/erickpeirson/Programming/genecology/main/data/testdata.xgmml', 'r') as f:
            self.data = f.read()

        self.processor = VogonXGMMLProcessor()
        self.network = Network(label='test')
        self.network.save()
        
    def test_process(self):
        print self.processor.process(self.data, self.network.id)


class TestAuthorities(TestCase):
    def setUp(self):
        self.namespace = '{http://www.digitalhps.org/}'

    def test_get_by_namespace(self):
        managers = authorities.get_by_namespace(self.namespace)
        self.assertGreater(len(managers), 0)
        self.assertEqual(managers[0], authorities.ConceptpowerAuthority)

    def test_resolve_concept(self):
        # Should respond to Concept post_save signal.
        c = Concept(uri='http://www.digitalhps.org/concepts/CON536b243d-3c71-4a5c-ab79-3c7f12765b3f')
        c.save()

        # Reload the Concept instance for inspection.
        c_ = Concept.objects.get(pk=c.id)

        self.assertEqual(c_.label, 'Sir Harry Godwin')
        self.assertEqual(c_.typed.uri, 'http://www.digitalhps.org/types/TYPE_986a7cc9-c0c1-4720-b344-853f08c136ab')
        self.assertEqual(c_.authority, 'ConceptpowerAuthority')
        self.assertTrue(c_.resolved)
        self.assertFalse(c_.description is None)

    def test_resolve_type(self):
        t = Type(uri='http://www.digitalhps.org/types/TYPE_986a7cc9-c0c1-4720-b344-853f08c136ab')
        t.save()

        t_ = Type.objects.get(pk=t.id)

        self.assertEqual(t_.label, 'E21 Person')
        self.assertEqual(t_.authority, 'ConceptpowerAuthority')
        self.assertTrue(t_.resolved)
        self.assertFalse(t_.description is None)

    def test_get_or_create_type(self):
        t = Type.objects.get_or_create(uri='http://www.digitalhps.org/types/TYPE_986a7cc9-c0c1-4720-b344-853f08c136ab')[0]

        t_ = Type.objects.get(pk=t.id)

        self.assertEqual(t_.label, 'E21 Person')
        self.assertEqual(t_.authority, 'ConceptpowerAuthority')
        self.assertTrue(t_.resolved)
        self.assertFalse(t_.description is None)

