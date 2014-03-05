from django.db import models

class TextPosition(models.Model):
    startposition = models.IntegerField(default=0)
    endposition = models.IntegerField(default=0)
    text = models.ForeignKey('texts.Text')

class Appellation(models.Model):
    concept = models.ForeignKey('concepts.Concept')
    textposition = models.ForeignKey('TextPosition')

class Relation(models.Model):
    source = models.ForeignKey('Appellation', related_name='relation_source')
    target = models.ForeignKey('Appellation', related_name='relation_target')
    predicate = models.ForeignKey('Appellation',
                                  related_name='relation_predicate')