from django.db import models

class Text(models.Model):
    uri = models.CharField(max_length=500)
    filename = models.CharField(max_length=200)
#    source = models.ForeignKey(Repository, blank=True, null=True)

    title = models.CharField(max_length=500)
    
    dateCreated = models.DateField()
    dateDigitized = models.DateField()
    dateAdded = models.DateField(auto_now_add=True)
    dateModified = models.DateField(auto_now=True)

    creator = models.ManyToManyField('concepts.Concept', through='Creator') # Presumably a person.

    content = models.TextField()
    length = models.IntegerField(default=0)

class Creator(models.Model):
    concept = models.ForeignKey('concepts.Concept')
    text = models.ForeignKey(Text, related_name='creator_text')
