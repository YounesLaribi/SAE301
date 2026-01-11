from abc import ABC, abstractmethod

class RoleDAOInterface(ABC):
    @abstractmethod
    def create(self, role):
        pass

    @abstractmethod
    def get_by_id(self, id_role):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, role):
        pass

    @abstractmethod
    def delete(self, id_role):
        pass
