from app.models.Planning import Planning
from app.models.PlanningDAOInterface import PlanningDAOInterface
from app.extensions import db

class PlanningDAO(PlanningDAOInterface):
    def create(self, planning):
        db.session.add(planning)
        db.session.commit()
        return planning

    def get_by_id(self, date_heure, id_media):
        return Planning.query.get((date_heure, id_media))

    def get_all(self):
        return Planning.query.all()

    def update(self, planning):
        db.session.commit()
        return planning

    def delete(self, date_heure, id_media):
        planning = self.get_by_id(date_heure, id_media)
        if planning:
            db.session.delete(planning)
            db.session.commit()
