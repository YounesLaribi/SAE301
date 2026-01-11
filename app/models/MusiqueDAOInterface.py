from abc import ABC, abstractmethod

class MusiqueDAOInterface(ABC):
    @abstractmethod
    def create(self, musique):
        pass

    @abstractmethod
    def get_by_id(self, id_musique):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, musique):
        pass

    @abstractmethod
    def delete(self, id_musique):
        pass
