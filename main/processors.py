from django.core.exceptions import ObjectDoesNotExist

from .parsers import *
from .models import *
from concepts.models import *

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

processor_choices = (
    ('VogonXGMMLProcessor', 'Vogon XGMML'),
)

class BaseProcessor(object):
    appellations = {}
    nodes = {}

    def __init__(self):
        self.parser = self.parser_class()

    def process(self, rawdata, network_id):
        """
        Load network data from an annotation dataset.
        
        Parameters
        ----------
        rawdata : str
        network_id : int
        
        Returns
        -------
        nodes : :class:`django.db.models.query.QuerySet`
            QuerySet containing all :class:`.Node`\s generated or
            updated in this operation.
        edges : :class:`django.db.models.query.QuerySet`
            QuerySet containing all :class:`.Edge`\s generated or
            updated in this operation.
        annotations : :class:`django.db.models.query.QuerySet`
            QuerySet containing all :class:`.Annotation`\s generated in this
            operation.
        """
        
        logger.debug('Process data for network {0}.'.format(network_id))
        self.network = Network.objects.get(pk=network_id)
        
        self.accession = Accession(part_of=self.network)
        self.accession.save()
        logger.debug('Created accession {0}.'.format(self.accession.id))
        
        self.data = self.parser.Parse(rawdata)

        logger.debug(
            'Processing {0} appellations and {1} relations'.format(
                len(self.data['appellations']), len(self.data['relations'])))
        self.handle_appellations(self.data['appellations'])
        self.handle_relations(self.data['relations'])

        nodes = Node.objects.filter(part_of__id=network_id)
        edges = Edge.objects.filter(part_of__id=network_id)
        annotations = Annotation.objects.filter(
                                            in_accession_id=self.accession.id)

        return nodes, edges, annotations
    

    def handle_appellation(self, datum):
        """
        Generate an :class:`.Appellation` an its corresponding 
        :prop:`.interpretation`\.
        
        Parameters
        ----------
        datum : dict
            Parsed datum containing an ``attributes`` subdict.
            
        Returns
        -------
        appellation : :class:`.Appellation`
        interpretation : :class:`.Concept`
        """
        text = Text.objects.get_or_create(
                        uri=datum['attributes']['text'])[0]

        interpretation = Concept.objects.get_or_create(
                        uri=datum['attributes']['concept'])[0]
                        
        # Get the Concept Type, if available.
        if 'type' in datum['attributes']:
            if datum['attributes']['type'] != 'None':
                type = Type.objects.get_or_create(
                                uri=datum['attributes']['type'])[0]
                interpretation.typed = type
        
        appellation = Appellation(
                        text=text,
                        interpretation=interpretation,
                        in_accession=self.accession,
                        )

        if 'startposition' in datum['attributes']:
            start_position = datum['attributes']['startposition']
            if start_position != -1:
                appellation.start_position = start_position
        if 'endposition' in datum['attributes']:
            end_position = datum['attributes']['endposition']
            if end_position != -1:
                appellation.end_position = end_position
                
        if 'label' in datum:
            appellation.label = datum['label']
        elif 'label' in datum['attributes']:
            appellation.label = datum['attributes']['label']
        if interpretation.label is None and appellation.label is not None:
            interpretation.label = appellation.label

        interpretation.save()
        appellation.save()

        return appellation, interpretation

    def handle_element(self, element, datum, evidence):
        """
        Adds :prop:`.evidence` to a :class:`.NetworkElement`\.
        
        Parameters
        ----------
        element : :class:`.NetworkElement`
            Or a subclass.
        datum : dict
            Parsed datum from which ``evidence`` is derived.
        evidence : :class:`.Annotation`
            Should be a subclass, :class:`.Appellation` or :class:`.Relation`\.
            
        Returns
        -------
        None
        """
        
        if element.label is None:
            if 'label' in datum:
                element.label = datum['label']
            elif 'label' in datum['attributes']:
                element.label = datum['attributes']['label']
    
        element.evidence.add(evidence)
        element.save()

    def handle_appellations(self, data):
        """
        Process parsed appellation data.
        
        Parameters
        ----------
        data : list
            Contains parsed data dicts.
        
        Returns
        -------
        None
        """
        
        for datum in data:
            appellation, interpretation = self.handle_appellation(datum)

            try:
                node = Node.objects.get(represents__id=interpretation.id, part_of__id=self.network.id)
            except ObjectDoesNotExist:
                node = Node(
                    represents=interpretation,
                    part_of=self.network,
                )
                node.save()
            self.handle_element(node, datum, appellation)

            self.appellations[datum['id']] = appellation
            self.nodes[datum['id']] = node

    def handle_relations(self, data):
        """
        Generate :class:`.Relation`\s and create/update corresponding
        :class:`.Edge`\s.
        
        Parameters
        ----------
        data : list
            A list of parsed data dicts describing relations.
        
        Returns
        -------
        None
        
        """
        
        for datum in data:
            appellation, interpretation = self.handle_appellation(datum)

            source = self.appellations[datum['source']]
            target = self.appellations[datum['target']]

            relation = Relation(
                            source=source,
                            predicate=appellation,
                            target=target,
                            in_accession=self.accession
                            )
                            
            if 'label' in datum:
                relation.label = datum['label']
            elif 'label' in datum['attributes']:
                relation.label = datum['attributes']['label']
            relation.save()

            source_node = self.nodes[datum['source']]
            target_node = self.nodes[datum['target']]
            try:
                edge = Edge.objects.get(
                        source__id=source_node.id,
                        target__id=target_node.id,
                        represents__id=interpretation.id,
                        part_of__id=self.network.id
                        )
            except ObjectDoesNotExist:
                edge = Edge(
                    source = source_node,
                    target = target_node,
                    represents = interpretation,
                    part_of = self.network,
                )
                edge.save()
                                
            self.handle_element(edge, datum, relation)

class VogonXGMMLProcessor(BaseProcessor):
    parser_class = VogonXGMMLParser

