from abc import ABC, abstractmethod

class PlanningDAOInterface(ABC):
    @abstractmethod
    def create(self, planning):
        pass

    @abstractmethod
    def get_by_id(self, date_heure, id_media):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, planning):
        pass

    @abstractmethod
    def delete(self, date_heure, id_media):
        pass
