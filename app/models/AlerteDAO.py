from app.models.Alerte import Alerte
from app.models.AlerteDAOInterface import AlerteDAOInterface
from app.extensions import db

class AlerteDAO(AlerteDAOInterface):
    def create(self, alerte):
        db.session.add(alerte)
        db.session.commit()
        return alerte

    def get_by_id(self, id_alerte):
        return Alerte.query.get(id_alerte)

    def get_all(self):
        return Alerte.query.all()

    def update(self, alerte):
        db.session.commit()
        return alerte

    def delete(self, id_alerte):
        alerte = self.get_by_id(id_alerte)
        if alerte:
            db.session.delete(alerte)
            db.session.commit()
