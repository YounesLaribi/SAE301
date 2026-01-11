from abc import ABC, abstractmethod

class PlaylistDAOInterface(ABC):
    @abstractmethod
    def create(self, playlist):
        pass

    @abstractmethod
    def get_by_id(self, id_playlist):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, playlist):
        pass

    @abstractmethod
    def delete(self, id_playlist):
        pass
