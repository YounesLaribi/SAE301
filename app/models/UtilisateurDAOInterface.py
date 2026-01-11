from abc import ABC, abstractmethod

class UtilisateurDAOInterface(ABC):
    @abstractmethod
    def create(self, utilisateur):
        pass

    @abstractmethod
    def get_by_id(self, id_utilisateur):
        pass

    @abstractmethod
    def get_by_username(self, username):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, utilisateur):
        pass

    @abstractmethod
    def delete(self, id_utilisateur):
        pass
