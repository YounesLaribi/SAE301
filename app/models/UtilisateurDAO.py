from app.models.Utilisateur import Utilisateur
from app.models.UtilisateurDAOInterface import UtilisateurDAOInterface
from app.extensions import db

class UtilisateurDAO(UtilisateurDAOInterface):
    def create(self, utilisateur):
        db.session.add(utilisateur)
        db.session.commit()
        return utilisateur

    def get_by_id(self, id_utilisateur):
        return Utilisateur.query.get(id_utilisateur)

    def get_by_username(self, username):
        return Utilisateur.query.filter_by(username=username).first()

    def get_all(self):
        return Utilisateur.query.all()

    def update(self, utilisateur):
        db.session.commit()
        return utilisateur

    def delete(self, id_utilisateur):
        utilisateur = self.get_by_id(id_utilisateur)
        if utilisateur:
            db.session.delete(utilisateur)
            db.session.commit()
