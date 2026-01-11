from abc import ABC, abstractmethod

class MediaDAOInterface(ABC):
    @abstractmethod
    def create(self, media):
        pass

    @abstractmethod
    def get_by_id(self, id_media):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, media):
        pass

    @abstractmethod
    def delete(self, id_media):
        pass
