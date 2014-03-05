from django.db import models

class Concept(models.Model):
    uri = models.CharField(max_length=500, unique=True)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)