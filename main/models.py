from django.db import models
from django.contrib.contenttypes.models import ContentType

optional = { 'blank': True, 'null': True }

class HeritableObject(models.Model):
    """
    An object that is aware of its "real" type, i.e. the subclass that it 
    instantiates.
    """
    
    real_type = models.ForeignKey(ContentType, editable=False)
    label = models.CharField(max_length=255, **optional)

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(HeritableObject, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def cast(self):
        """
        Re-cast this object using its "real" subclass.
        """

        return self.real_type.get_object_for_this_type(pk=self.pk)

    def __unicode__(self):
        return unicode(self.label)

    class Meta:
        abstract = True

class Researcher(HeritableObject):
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, **optional)
    link = models.URLField(max_length=255, **optional)
    photo = models.FileField(**optional)
    bio = models.TextField(**optional)

class Network(HeritableObject):
    pass
    
class NetworkElement(HeritableObject):
    represents = models.ForeignKey('concepts.Concept')
    evidence = models.ManyToManyField('Annotation', **optional)
    part_of = models.ForeignKey('Network')
    
    class Meta:
        abstract = True

class Node(NetworkElement):
    pass

class Edge(NetworkElement):
    source = models.ForeignKey('Node', related_name='edges_from')
    target = models.ForeignKey('Node', related_name='edges_to')

    def __unicode__(self):
        return u'{0} - {1} - {2}'.format(self.source.label, self.label, self.target.label)

class NodeBundle(NetworkElement):
    contains = models.ManyToManyField('Node', related_name='in_bundles')

class EdgeBundle(NetworkElement):
    contains = models.ManyToManyField('Edge', related_name='in_bundles')

class Accession(HeritableObject):
    created = models.DateTimeField(auto_now_add=True)
    part_of = models.ForeignKey('Network')

    def __unicode__(self):
        return u'{0}'.format(self.created)

class Annotation(HeritableObject):
    in_accession = models.ForeignKey('Accession')
    made_by = models.ForeignKey(
                        'Researcher', related_name='contributions', **optional)

class Relation(Annotation):
    source = models.ForeignKey('Appellation', related_name='relations_from')
    predicate = models.ForeignKey('Appellation', related_name='relations_with')
    target = models.ForeignKey('Appellation', related_name='relations_to')

    start = models.DateField(**optional)
    occur = models.DateField(**optional)
    end = models.DateField(**optional)

    def __unicode__(self):
        return u'{0} - {1} - {2} in {3}'.format(self.source.label, self.label, self.target.label, self.predicate.text)

class Appellation(Annotation):
    start_position = models.IntegerField(**optional)
    end_position = models.IntegerField(**optional)
    text = models.ForeignKey('Text', related_name='annotations')
    interpretation = models.ForeignKey(
                            'concepts.Concept', related_name='representations')
                            
    def __unicode__(self):
        return u'{0} in {1}'.format(self.interpretation.label, self.text.uri)

class Text(HeritableObject):
    # TODO: add some basic metadata fields (esp. creator).
    uri = models.CharField(max_length=255)
    content_url = models.URLField(max_length=255, **optional)

    content = models.TextField()
    length = models.IntegerField(default=0)
    
    restricted = models.BooleanField(default=True)

    creators = models.ManyToManyField('concepts.Concept')


    def __unicode__(self):
        return u'{0}'.format(self.uri)



class Layout(HeritableObject):
    describes = models.ForeignKey('Network')

class NodePosition(HeritableObject):
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField(default=0)
    size = models.FloatField(default=1)
    
    # TODO: implement colors.
#    r = models.IntegerField()
#    g = models.IntegerField()
#    b = models.IntegerField()

    describes = models.ForeignKey('Node')
    describes_by_id = models.IntegerField(**optional)
    describes_by_label = models.CharField(max_length=255, **optional)

    part_of = models.ForeignKey('Layout')

    def save(self, *args, **kwargs):
        """
        Store the ID of the Node that this NodePosition describes, for faster
        lookup.
        """
        if self.describes is not None:
            self.describes_by_id = self.describes.id
            self.describes_by_label = self.describes.label

        super(NodePosition, self).save(*args, **kwargs)

class EdgePosition(HeritableObject):
    x_source = models.IntegerField()
    x_target = models.IntegerField()
    y_source = models.IntegerField()
    y_target = models.IntegerField()
    z = models.IntegerField(default=0)
    width = models.IntegerField(default=1)

    describes = models.ForeignKey('Edge')

    part_of = models.ForeignKey('Layout')

