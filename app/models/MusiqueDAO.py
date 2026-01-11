from app.models.Musique import Musique
from app.models.MusiqueDAOInterface import MusiqueDAOInterface
from app.extensions import db

class MusiqueDAO(MusiqueDAOInterface):
    def create(self, musique):
        db.session.add(musique)
        db.session.commit()
        return musique

    def get_by_id(self, id_musique):
        return Musique.query.get(id_musique)

    def get_all(self):
        return Musique.query.all()

    def update(self, musique):
        db.session.commit()
        return musique

    def delete(self, id_musique):
        musique = self.get_by_id(id_musique)
        if musique:
            db.session.delete(musique)
            db.session.commit()
