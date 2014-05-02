from django.db import models

class Text(models.Model):
    uri = models.CharField(max_length=500, unique=True)
    filename = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=500)
    
    dateCreated = models.DateField()
    dateDigitized = models.DateField()
    dateAdded = models.DateField(auto_now_add=True)
    dateModified = models.DateField(auto_now=True)

    creator = models.ManyToManyField('concepts.Concept') # Presumably a person.

    content = models.TextField()
    length = models.IntegerField(default=0)
    
    restricted = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "texts"
