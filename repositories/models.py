"""
Provides methods for retrieving :class:`.Text` and metadata from remote
repositories.

.. autosummary::

   Repository
   Credential
   
"""

from django.db import models
import repository  # Who knows what's in there?

class Repository(models.Model):
    """
    Represents a RESTful service for retrieving :class:`.Text`\.
    
    Attributes
    ----------
    name : str
        A human-readable na,e
    manager : str
        The name of a management module in :mod:`repositories.repository`\.
    endpoint : str
        The URL endpoint of the RESTful service.
    """
    name = models.CharField(max_length=200)
    manager = models.CharField(max_length=200)
    endpoint = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "repositories"

    def get_manager(self):
        """
        Retrieves a repository manager from :mod:`repositories.repository`\.
        """
        return repository.managers[self.manager]

class Credential(models.Model):
    """
    Represents an access credential for a :class:`.Repository`\.
    
    Attributes
    ----------
    repository :
        OneToOne reference to a :class:`.Repository`\.
    private_key : str
        The private authentication key for the :class:`.Repository`\.
    public_key : str
        The public authentication key for the :class:`.Repository`\.
    """
    repository = models.OneToOneField(Repository)
    private_key = models.CharField(max_length=200)
    public_key = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "credentials"