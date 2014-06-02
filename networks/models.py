"""
Represents network entities and their evidence.

.. autosummary::

   Node
   Edge
   Network
   Appellation
   Relation
   TextPosition
   Dataset
   Layout
   NodePosition   
   NetworkProjection
   ProjectionMapping
   NodeManager
   NodeTypeManager
   

"""

from django.db import models
from concepts.models import Concept
from django.core.exceptions import ObjectDoesNotExist

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

class NodeManager(models.Manager):
    """
    Class for managing :class:`.Node`\.
    """
    def get_unique(self, concept):
        """
        Get or create a :class:`.Node` for a particular :class:`.Concept`\.
        
        If a :class:`.Node` already exists for ``concept``, then return it.
        Otherwise, create a new :class:`.Node`\.
        
        Parameters
        ----------
        concept : 
            A :class:`.Concept` instance.
        """
        try:
            node = Node.objects.get(concept=concept.id)
            logger.debug('Found node for {0}'.format(concept.name))
        except Node.DoesNotExist:
            logger.debug(u'Node does not exist for {0}, creating.'
                                                          .format(concept.name))
            node = Node(concept=concept)
            node.save()

        return node

class Node(models.Model):
    """
    A vertex in one or more :class:`.Network`\.
    
    A :class:`.Node` can be associated with zero or more :class:`.Appellation` 
    instances, which represent the instantiation of its ``concept`` in a text.
    
    Attributes
    ----------
    appellations :
        ManyToMany reference to :class:`.Appellation`\.
    concept : 
        ForeignKey reference to a :class:`.Concept`\.
    type :
        ForeignKey reference to a :class:`.NodeType` (optional).
    objects :
        :class:`.NodeManager` instance.
    """
        
    appellations = models.ManyToManyField('networks.Appellation')
    concept = models.ForeignKey('concepts.Concept')
    type = models.ForeignKey('networks.NodeType', blank=True, null=True)

    objects = NodeManager()

    def __unicode__(self):
        return unicode(self.concept.name)

    def save(self, *args, **kwargs):
        """
        On creation, retrieves and associates a :class:`.NodeType` based on the
        values of ``name`` and ``uri``.
        """
        if self.pk is None:
            self.type = NodeType.objects.get_unique(self.concept.type.name,
                                                    self.concept.type.uri)
        super(Node, self).save(*args, **kwargs)

class Network(models.Model):
    """
    A set of :class:`.Node` and :class:`.Edge`\.
    
    Attributes
    ----------
    name : str
        A human-readable name.
    nodes : 
        ManyToMany reference to :class:`.Node`\.
    edges : 
        ManyToMany reference to :class:`.Edge`\.
    layout :
        ManyToMany reference to :class:`.Layout`\.
    """

    name = models.CharField(max_length='200')
    nodes = models.ManyToManyField('networks.Node')
    edges = models.ManyToManyField('networks.Edge')
    
    layout = models.ManyToManyField('networks.Layout', blank=True, null=True)

    def __unicode__(self):
        return self.name

class NodeTypeManager(models.Manager):
    """
    Class for managing :class:`.NodeType`\.
    """
    def get_unique(self, name, uri=None):
        """
        Get or create a :class:`.NodeType`\.
        
        If :class:`.NodeType` already exists with that URI, return it. Otherwise
        create a new one.
        
        Parameters
        ----------
        name : str
            A human-readable name.
        uri : str
            A URI, presumably in the namespace of a :class:`.ConceptAuthority`\.
        """

        try:
            instance = NodeType.objects.filter(uri=uri).get()
            logger.debug('NodeType for {0} exists.'.format(uri))
        except ObjectDoesNotExist:
            logger.debug('NodeType for {0} does not exist. Creating.'
                                                                   .format(uri))
            instance = NodeType(name=name,
                                uri=uri)
            instance.save()
        return instance

class NodeType(models.Model):
    """
    An ontological concept for classifying :class:`.Node`\.
    
    Conventionally, but not exclusively, correponds to instances of 
    :class:`.ConceptType`\.
    
    Attributes
    ----------
    name : str
        A human-readable name.
    uri : str
        URI, presumably in the ``namespace`` of a :class:`.ConceptAuthority`\.
    objects : 
        Instance of :class:`.NodeTypeManager`\.
    """

    name = models.CharField(max_length='200')
    uri = models.CharField(max_length='500', null=True, blank=True)

    objects = NodeTypeManager()
    
    def __unicode__(self):
        return self.name

class NetworkProjection(models.Model):  
    """
    A set of rules for simplifying or abstracting networks.
    
    Attributes
    ----------
    name : str
        A human-readable name.
    network : 
        ForeignKey reference to a :class:`.Network`\.
    mappings : 
        ManyToMany reference to :class:`.ProjectionMapping`\.
    """
    name = models.CharField(max_length='200')
    network = models.ForeignKey('networks.Network')
    
    mappings = models.ManyToManyField('networks.ProjectionMapping')
    
    def __unicode__(self):
        return unicode(self.name)
    
class ProjectionMapping(models.Model):
    """
    A rule about how to collapse :class:`.Node` instances in a
    :class:`.Network`\.
    
    For example, we may wish to collapse all :class:`.Node` representing people
    into a smaller set of :class:`.Node` representing the institutions with
    which they are affiliated. In that case, ``primaryNode`` would refer to
    a :class:`.NodeType` representing institutions, and ``secondaryNode`` would 
    refer to a :class:`.NodeType` representing persons.
    
    Attributes
    ----------
    primaryNode : 
        ForeignKey relation to a :class:`.NodeType`\. The :class:`.Node` to subsume ``secondaryNodes``.
    secondaryNodes :
        ManyToMany relation to :class:`.NodeType`\. These :class:`.Node` are subsumed by ``primaryNode``.
    """
    primaryNode = models.ForeignKey('networks.NodeType', 
                                    related_name='projection_nodeType')
    secondaryNodes = models.ManyToManyField('networks.NodeType',
                                            related_name='projection_collapse')

    def __unicode__(self):
        return u'{0}: {1}'.format(self.primaryNode.name,
                            [ str(s.name) for s in self.secondaryNodes.all() ])

class Edge(models.Model):
    """
    A directed link between two :class:`.Node`\.
    
    Attributes
    ----------
    source : 
        ForeignKey reference to a :class:`.Node`\.
    target :
        ForeignKey reference to a :class:`.Node`\.
    relations :
        ManyToMany reference to :class:`.Relation`\, which are the instantiations of this edge in text(s).
    concept : 
        ForeignKey reference to a :class:`.Concept`\. e.g. "engaged with."
    """

    source = models.ForeignKey('networks.Node', related_name='edge_source')
    target = models.ForeignKey('networks.Node', related_name='edge_target')

    relations = models.ManyToManyField('networks.Relation')
    concept = models.ForeignKey('concepts.Concept')

    def __unicode__(self):
        return unicode(u'{0} - {1} - {2}'.format(self.source.concept.name,
                                                 self.concept.name,
                                                 self.target.concept.name))

class TextPosition(models.Model):
    """
    A position in a :class:`.Text` on which :class:`.Appellation` are anchored.
    
    Attributes
    ----------
    startposition : int
        The 0-based index where the position begins.
    endtposition : int
        The 0-based index where the position ends (exclusive).
    text :
        ForeignKey reference to the :class:`.Text` in which this :class:`.TextPosition` is found.
    """

    startposition = models.IntegerField(default=0)
    endposition = models.IntegerField(default=0)
    text = models.ForeignKey('texts.Text')

    class Meta:
        verbose_name_plural = "text positions"

class Dataset(models.Model):
    """
    A set of :class:`.Appellation` and :class:`.Relation` and their associated :class:`.Network`\.
    
    Attributes
    ----------
    name : str
        A human-readable name.
    appellations :
        ManyToMany reference to :class:`.Appellation`\.
    relations :
        ManyToMany reference to :class:`.Relation`\.
    networks : 
        ManyToMany reference to :class:`.Network`\.
    added : datetime
        Datetime when :class:`.Dataset` was created.
    """
    name = models.CharField(max_length=200)
    appellations = models.ManyToManyField('networks.Appellation')
    relations = models.ManyToManyField('networks.Relation')

    networks = models.ManyToManyField('networks.Network', through='NetworkLink')

    added = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.name

class NetworkLink(models.Model):
    """
    Passthrough linkage for :class:`.Network` and :class:`Dataset`\.
    
    Attributes
    ----------
    network :
        ForeignKey relation to :class:`.Network`\.
    dataset : 
        ForeignKey relation to :class:`.Dataset`\.
    added : datetime
        Datetime when :class:`.NetworkLink` was created.
    """
    network = models.ForeignKey('networks.Network',
                                related_name='linked_network')
    dataset = models.ForeignKey('networks.Dataset',
                                related_name='linked_dataset')

    added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(u'Network: {0}; Dataset: {1}'.format(self.network.name,
                                                             self.dataset.name))

class Appellation(models.Model):
    """
    Represents an instantiation of a :class:`.Concept` in a :class:`.Text`\.
    
    Attributes
    ----------
    concept :
        (optional) ForeignKey relation to a :class:`.Concept`\.
    textposition : 
        (optional) ForeignKey relation to a :class:`.TextPosition`\.
    """
    concept = models.ForeignKey('concepts.Concept', blank=True, null=True)
    textposition = models.ForeignKey('TextPosition', null=True, blank=True)

    class Meta:
        verbose_name_plural = "appellations"

    def __unicode__(self):
        return unicode(self.concept.name)

class Relation(models.Model):
    """
    Represents an instantiation of an association between two :class:`.Concept`
    in a :class:`.Text`\.
    
    Attributes
    ----------
    source : 
        ForeignKey relation to a :class:`.Appellation`\.
    target :
        ForeignKey relation to a :class:`.Appellation`\.
    predicate :
        ForeignKey relation to a :class:`.Appellation`\, representing the
        evidentiary basis for the inferred association.
    """
        
    source = models.ForeignKey('Appellation', related_name='relation_source')
    target = models.ForeignKey('Appellation', related_name='relation_target')
    predicate = models.ForeignKey('Appellation',
                                  related_name='relation_predicate')
                                  
    class Meta:
        verbose_name_plural = "relations"

    def __unicode__(self):
        return unicode(u'{0} - {1} - {2}'.format(self.source.concept.name,
                                                 self.predicate.concept.name,
                                                 self.target.concept.name))

class Layout(models.Model):
    """
    A set of :class:`.NodePosition` describing the layout of a
    :class:`.Network`\.
    
    Attributes
    ----------
    name : str
        A human-readable name.
    positions :
        ManyToMany reference to :class:`.NodePosition`\.
    """
    name = models.CharField(max_length=200)
    positions = models.ManyToManyField('networks.NodePosition', null=True,
                                                                blank=True)

    def __unicode__(self):
        return unicode(self.name)

class NodePosition(models.Model):
    """
    Represents the x,y position of a :class:`.Node` in a unit-less 2D space.
    
    Attributes
    ----------
    node : 
        ForeignKey reference to :class:`.Node`
    x : float
        The position of ``node`` in the X dimension.
    y : float
        The position of ``node`` in the Y dimension.        
    """
    node = models.ForeignKey('networks.Node', related_name='layout_node')
    x = models.DecimalField(decimal_places=6, max_digits=12)
    y = models.DecimalField(decimal_places=6, max_digits=12)

    def __unicode__(self):
        return unicode(self.node.concept.name)


