from app.models.Lecteur import Lecteur
from app.models.LecteurDAOInterface import LecteurDAOInterface
from app.extensions import db

class LecteurDAO(LecteurDAOInterface):
    def create(self, lecteur):
        db.session.add(lecteur)
        db.session.commit()
        return lecteur

    def get_by_id(self, id_lecteur):
        return Lecteur.query.get(id_lecteur)

    def get_all(self):
        return Lecteur.query.all()

    def update(self, lecteur):
        db.session.commit()
        return lecteur

    def delete(self, id_lecteur):
        lecteur = self.get_by_id(id_lecteur)
        if lecteur:
            db.session.delete(lecteur)
            db.session.commit()
