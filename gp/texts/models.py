from django.db import models

class Text(models.Model):
    uri = models.CharField(max_length=500)
    filename = models.CharField(max_length=200)
    title = models.CharField(max_length=500)
    
    dateCreated = models.DateField()
    dateDigitized = models.DateField()
    dateAdded = models.DateField(auto_now_add=True)
    dateModified = models.DateField(auto_now=True)

    creator = models.ManyToManyField('concepts.Concept') # Presumably a person., through='Creator'

    content = models.TextField()
    length = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "texts"
