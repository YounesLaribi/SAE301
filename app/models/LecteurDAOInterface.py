from abc import ABC, abstractmethod

class LecteurDAOInterface(ABC):
    @abstractmethod
    def create(self, lecteur):
        pass

    @abstractmethod
    def get_by_id(self, id_lecteur):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, lecteur):
        pass

    @abstractmethod
    def delete(self, id_lecteur):
        pass
