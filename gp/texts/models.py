from django.db import models

class Text(models.Model):
    uri = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    length = models.IntegerField(default=0)
    creator = models.ManyToManyField('concepts.Concept') # Presumably a person.
    content = models.TextField()
