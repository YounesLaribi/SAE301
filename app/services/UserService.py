# Service gérant la création et la suppression des utilisateurs et des rôles.
from app.models.Utilisateur import Utilisateur
from app.extensions import db
from app.models.Role import Role

class UserService:
    def get_all_users(self):
        return Utilisateur.query.all()
    
    def get_all_roles(self):
        return Role.query.all()
        
    def create_user(self, username, password, role_id):
        if Utilisateur.query.filter_by(username=username).first():
            return False, "Cet utilisateur existe déjà."
            
        user = Utilisateur(username=username, id_role=role_id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return True, f"Utilisateur {username} créé."
        
    def delete_user(self, user_id, current_user):
        user = Utilisateur.query.get_or_404(user_id)
        
        if user.username == 'admin':
             return False, "Impossible de supprimer l'admin principal"
             
        if user.role.nom == 'Admin' and current_user.username != 'admin':
             return False, "Seul le super-admin peut supprimer un autre admin."

        db.session.delete(user)
        db.session.commit()
        return True, "Utilisateur supprimé."
