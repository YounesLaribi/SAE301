from app.models.Utilisateur import Utilisateur
from app.extensions import db
from datetime import datetime

class AuthService:
    def authenticate_user(self, username, password):
        """
        Vérifie les identifiants de l'utilisateur.
        Retourne l'objet utilisateur si valide, sinon None.
        """
        user = Utilisateur.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Mise à jour de la date de dernière connexion
            user.last_login = datetime.now()
            db.session.commit()
            return user
        return None
