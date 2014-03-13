from repositories.models import Repository, Credential

class RepositoryManager(object):

    def __init__(self, cred):
        """
        cred : :class:`.repositories.models.Credential`
        """

        R = cred.repository.get_manager()

        self.manager = R(   cred.public_key,
                            cred.private_key,
                            cred.repository.endpoint )

    def list_collections(self):
        return self.manager.list_collections()

    def list_items(self, collection):
        """
        collection : int
            collection entityId
        """
        return self.manager.list_items()
