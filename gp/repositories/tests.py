"""
Tests for Repositories app.
"""

from django.test import TestCase
from managers import RepositoryManager
from models import Repository, Credential
from repository.dspace import DSpace
from settings import *

def create_repository():
    repository = Repository(name="TestRepository",
                            manager="DSpace",
                            endpoint="http://dstools.hpsrepository.asu.edu/rest/")
    repository.save()
    return repository

def create_credential(repo):
    credential = Credential(repository_id = repo.id,
                            private_key = PRIVATE_KEY,
                            public_key = PUBLIC_KEY )
    credential.save()
    return credential


class DSpaceManagerTests(TestCase):
    """
    tests for repositories.repository.dspace
    """

    def setUp(self):
        self.repo = create_repository()   # Creates a DSpace Repository

    def test_dspace_get_manager(self):
        manager = self.repo.get_manager()
        self.assertEqual(manager, DSpace)

class RepositoryManagerTests(TestCase):
    """
    tests for repositories.models.RepositoryManager
    """

    def setUp(self):
        self.repo = create_repository()
        self.cred = create_credential(self.repo)
        self.RepositoryManager = RepositoryManager(self.cred)

    def test_init(self):
        self.assertIsInstance(self.RepositoryManager.manager, DSpace)

    def test_list_collections(self):
        collections = self.RepositoryManager.list_collections()
        self.assertIsInstance(collections, list)
        self.assertIsInstance(collections[0], dict)