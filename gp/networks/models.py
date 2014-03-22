from django.db import models
from concepts.models import Concept

class Node(models.Model):
    appellations = models.ManyToManyField('networks.Appellation')
    concept = models.ForeignKey('concepts.Concept')

    def __unicode__(self):
        return unicode(self.concept.name)

class Network(models.Model):
    name = models.CharField(max_length='200')
    nodes = models.ManyToManyField('networks.Node')
    edges = models.ManyToManyField('networks.Edge')

    def __unicode__(self):
        return self.name

class Edge(models.Model):
    source = models.ForeignKey('networks.Node', related_name='edge_source')
    target = models.ForeignKey('networks.Node', related_name='edge_target')

    relations = models.ManyToManyField('networks.Relation')
    concept = models.ForeignKey('concepts.Concept')

    def __unicode__(self):
        return unicode('{0} - {1} - {2}'.format(self.source.concept.name,
                                                self.concept.name,
                                                self.target.concept.name))

class TextPosition(models.Model):
    startposition = models.IntegerField(default=0)
    endposition = models.IntegerField(default=0)
    text = models.ForeignKey('texts.Text')

    class Meta:
        verbose_name_plural = "text positions"

class Dataset(models.Model):
    name = models.CharField(max_length=200)
    appellations = models.ManyToManyField('networks.Appellation')
    relations = models.ManyToManyField('networks.Relation')

    networks = models.ManyToManyField('networks.Network', through='NetworkLink')

    added = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.name

class NetworkLink(models.Model):
    network = models.ForeignKey('networks.Network',
                                related_name='linked_network')
    dataset = models.ForeignKey('networks.Dataset',
                                related_name='linked_dataset')

    added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode('Network: {0}; Dataset: {1}'.format(self.network.name,
                                                           self.dataset.name))


class Appellation(models.Model):
    concept = models.ForeignKey('concepts.Concept')
    textposition = models.ForeignKey('TextPosition', null=True, blank=True)

    class Meta:
        verbose_name_plural = "appellations"

    def __unicode__(self):
        return unicode(self.concept.name)

class Relation(models.Model):
    source = models.ForeignKey('Appellation', related_name='relation_source')
    target = models.ForeignKey('Appellation', related_name='relation_target')
    predicate = models.ForeignKey('Appellation',
                                  related_name='relation_predicate')
                                  
    class Meta:
        verbose_name_plural = "relations"

    def __unicode__(self):
        return unicode('{0} - {1} - {2}'.format(self.source.concept.name,
                                                self.predicate.concept.name,
                                                self.target.concept.name))
