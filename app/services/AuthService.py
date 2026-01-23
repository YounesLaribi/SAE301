# Service gérant l'authentification des utilisateurs (login, vérification mot de passe).
from app.models.Utilisateur import Utilisateur

class AuthService:
    def authenticate_user(self, username, password):
        user = Utilisateur.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None
