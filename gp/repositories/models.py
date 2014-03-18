"""
Models for Repositories app.
"""

from django.db import models
import repository  # Who knows what's in there?

class Repository(models.Model):
    name = models.CharField(max_length=200)
    manager = models.CharField(max_length=200)
    endpoint = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "repositories"

    def get_manager(self):
        return repository.managers[self.manager]

class Credential(models.Model):
    repository = models.OneToOneField(Repository)
    private_key = models.CharField(max_length=200)
    public_key = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "credentials"