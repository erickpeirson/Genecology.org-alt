"""
managers for Networks app
"""

from django.utils.encoding import smart_text
from networks.models import Appellation, Relation, Network, Node, Edge, \
                            NetworkLink, TextPosition, Layout, NodePosition
from texts.models import Text

from concepts.managers import retrieve_concept
import networks.parsers as parsers #import parserFactory
from concepts.managers import retrieve_concept

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

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
        for datum in data['nodes']:
            appellation = self._add_appellation(datum, network)
            self.instance.appellations.add(appellation.id)

        for datum in data['edges']:
            relation = self._add_relation(datum, network)
            self.instance.relations.add(relation.id)
            self.instance.appellations.add(relation.predicate.id)

        self.instance.save()
        return self.instance

    def _add_appellation(self, datum, network):
        """
        checks to see whether a node exists for appellation.concept
        if not, create it.
        check if the node is in network
        if not, add it.
        """
        logger.debug(u'Handling appellation for {0}'.format(datum['id']))

        concept = retrieve_concept(datum['attributes']['concept'])
        logger.debug(u'Found concept {0}'.format(concept.name))

        # TODO: this is going to cause problems when editing. ID? Prevent?
        appellation = Appellation(concept=concept)
        appellation.save()
        
        # TODO: better way to do this (see relations block, below).
        self.these_appellations[datum['id']] = appellation

        # Check for, and attach, a TextPosition.
        instance = self._handle_text_position(appellation, datum)
        
        # Get Node and attach Appellation.
        node = Node.objects.get_unique(concept)
        node.appellations.add(appellation.id)
        node.save()
        
        self.these_nodes[datum['id']] = node
        
        # Check to see whether Node is in Network. If not, add it.
        if node not in network.nodes.all():
            logger.debug(u'Node for {0} not in Network {1}'
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
        logger.debug(u'Handling relation with source {0}.'
                                                   .format(datum['source']))

        # TODO: Problem. How to tell which appellations are referenced by
        #  the relation? Maybe text-position, but what if two appellations
        #  have the same position?
        #  Temporary solution is to assume that there is one appellation
        #  per concept....
        source = self.these_appellations[datum['source']]
        target = self.these_appellations[datum['target']]
        
        # Create appellation for predicate.
        # TODO: Find a better way to handle incomplete data.
        try:
            predicate_concept = retrieve_concept(datum['attributes']['predicate'])
        except KeyError:
            predicate_concept = retrieve_concept('http://www.digitalhps.org/concepts/CON42732c04-a08f-476b-97fb-646bb73cb54c')
        predicate = Appellation(concept=predicate_concept)
        predicate.save()
        
        # Check for text position.
        predicate = self._handle_text_position(predicate, datum)

        logger.debug(u'Relation: {0} - {1} - {2}'
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
            logger.debug(u'Edge not in Network {0}; adding.'
                                                          .format(network.name))
            network.edges.add(edge.id)

        return relation

    def _handle_text_position(self, instance, datum):
        try:    # There may not be any attributes, which is fine.
            if 'text' in datum['attributes'].keys():
                text_uri = datum['attributes']['text']
                # Get matching text.
                try:
                    text = Text.objects.get(uri=text_uri)
                except Text.DoesNotExist:
                    logger.warning('Text not found for {0}.'.format(text_uri))
                    text = None
                
                if text is not None:    # Can't have TextPsotion without Text.
                    position = TextPosition(text=text)
                    position.save()

                    # Start and end positions are not required.
                    if 'startposition' in datum['attributes'].keys()\
                     and 'endposition' in datum['attributes'].keys():
                        position.startposition = datum['attributes']\
                                                      ['startposition']
                        position.endposition = datum['attributes']\
                                                    ['endposition']
                        position.save()
                    instance.textposition = position
                    instance.save()

        except KeyError:
            pass

        return instance


def layout_create(layout, file, format):
    """
    Extract positional information from a network file, and create a new Layout.
    
    The nodes described in the network file should have IDs corresponding to
    nodes in an existing :class:`.Network` .
    
    Parameters
    ----------
    layout : :class:`.Layout`
        .
    file : str
        Path to a network file (e.g. a GraphML file).
    format : str
        Network data format (e.g. XGMML, GraphML)
    
    Returns
    -------
    :class:`.Layout`
        The resulting :class:`.Layout` object.
    """
    
    logger.debug('layout_create: {0}'.format(layout.name))
    
    parser = parsers.parserFactory(format)()
    data = parser.parse(file)
    
    for n in data['nodes']:
        # Find Node
        # TODO: handle exceptions (not found).
        node = Node.objects.get(pk=n['id'])
        
        # Create and associate a NodePosition.
        if 'x' in n['attributes'] and 'y' in n['attributes']:
            pos = NodePosition( node=node,
                                x = n['attributes']['x'],
                                y = n['attributes']['y'] )
            pos.save()
            layout.positions.add(pos.id)

    logger.debug('{0} positions found, out of {1} total nodes.'
                                       .format(len(layout.positions.all()),
                                               len(data['nodes'])))

    return layout


def layout_handle(layout, cleaned_data, formdata):
    """
    Handles uploaded network file and layout name.
    """
    file = cleaned_data['upload']
    name = formdata['name']
    
    # TODO: handle exceptions.
    network = Network.objects.get(pk=formdata['network'])

    format = formdata['format']
    
    layout = layout_create(layout, file, format)
    network.layout.add(layout)
    
    return layout