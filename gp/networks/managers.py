"""
managers for Networks app
"""


from networks.models import Appellation, Relation, Network, Node, Edge, NetworkLink
from concepts.managers import retrieve_concept
import networks.parsers as parsers #import parserFactory
from concepts.managers import retrieve_concept

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

class DatasetManager(object):
    these_appellations = {}
    these_nodes = {}

    def __init__(self, instance):
        self.instance = instance

    def add_dataset(self, cleaned_data, formdata):
        # Link network to dataset.
        network = Network.objects.get(pk=formdata['linked_dataset-0-network'])
        networklink = NetworkLink(network=network,
                                  dataset=self.instance)
        networklink.save()

        # Send data to parser based on specified format.
        format = cleaned_data['format']
        parser = parsers.parserFactory(format)()
        data = parser.parse(cleaned_data['upload'])

        # Check to see if network has nodes for the appellations and relations,
        #  and if not (create/)add them.
        for datum in data['appellations']:
            appellation = self._add_appellation(datum, network)
            self.instance.appellations.add(appellation.id)

        for datum in data['relations']:
            relation = self._add_relation(datum, network)
            self.instance.relations.add(relation.id)

        self.instance.save()
        return self.instance

    def _add_appellation(self, datum, network):
        """
        checks to see whether a node exists for appellation.concept
        if not, create it.
        check if the node is in network
        if not, add it.
        """
        logger.debug('Handling appellation for {0}'.format(datum['id']))

        concept = retrieve_concept(datum['id'])
        logger.debug('Found concept {0}'.format(concept.name))
        
        # TODO: check for text position.

        # TODO: this is going to cause problems when editing. ID? Prevent?
        appellation = Appellation(concept=concept)
        appellation.save()
        
        # TODO: better way to do this (see relations block, below).
        self.these_appellations[datum['id']] = appellation
        
        # Get Node and attach Appellation.
        node = Node.objects.get_unique(concept)
        node.appellations.add(appellation.id)
        node.save()
        
        self.these_nodes[datum['id']] = node
        
        # Check to see whether Node is in Network. If not, add it.
        if node not in network.nodes.all():
            logger.debug('Node for {0} not in Network {1}'
                                            .format(concept.name, network.name))
            network.nodes.add(node.id)

        return appellation

    def _add_relation(self, datum, network):
        """
        checks to see whether an edge exists for relation.concept
        if not, create it.
        check if the node is in network
        if not, add it.
        """
        logger.debug('Handling relation with source {0}.'
                                                   .format(datum['source']))

        # TODO: Problem. How to tell which appellations are referenced by
        #  the relation? Maybe text-position, but what if two appellations
        #  have the same position?
        #  Temporary solution is to assume that there is one appellation
        #  per concept....
        source = self.these_appellations[datum['source']]
        target = self.these_appellations[datum['target']]
        
        # Create appellation for predicate.
        predicate_concept = retrieve_concept(datum['attributes']['label'])
        predicate = Appellation(concept=predicate_concept)
        predicate.save()

        logger.debug('Relation: {0} - {1} - {2}'
                                             .format(source, predicate, target))
        relation = Relation(source=source,
                            target=target,
                            predicate=predicate)
        relation.save()

        source_node = self.these_nodes[datum['source']]
        target_node = self.these_nodes[datum['target']]

        try:
            edge = Edge.objects.get(source=source_node.id,
                                    target=target_node.id,
                                    concept=predicate_concept.id)
            logger.debug("edge found")
        except Edge.DoesNotExist:
            logger.debug("edge does not exist")
            edge = Edge(source=source_node,
                        target=target_node,
                        concept=predicate_concept)
            edge.save()
        edge.relations.add(relation.id)
        edge.save()
        
        if edge not in network.edges.all():
            logger.debug('Edge not in Network {0}; adding.'
                                                          .format(network.name))
            network.edges.add(edge.id)

        return relation