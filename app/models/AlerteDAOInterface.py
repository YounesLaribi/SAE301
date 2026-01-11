from abc import ABC, abstractmethod

class AlerteDAOInterface(ABC):
    @abstractmethod
    def create(self, alerte):
        pass

    @abstractmethod
    def get_by_id(self, id_alerte):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, alerte):
        pass

    @abstractmethod
    def delete(self, id_alerte):
        pass
