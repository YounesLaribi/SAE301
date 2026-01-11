from app.models.Utilisateur import Utilisateur
from app.models.Role import Role
from app.extensions import db

class UserService:
    def get_all_users(self):
        return Utilisateur.query.all()
    
    def get_all_roles(self):
        return Role.query.all()

    def create_user(self, username, password, role_id):
        if Utilisateur.query.filter_by(username=username).first():
            return False, "Cet utilisateur existe déjà."
        
        new_user = Utilisateur(username=username, id_role=role_id)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return True, f"Utilisateur {username} créé."

    def delete_user(self, user_id, deleter):
        user = Utilisateur.query.get(user_id)
        if not user:
             return False, "Utilisateur introuvable."
        
        # Protection du compte 'admin' principal (personne ne peut le supprimer)
        if user.username == 'admin':
            return False, "Impossible de supprimer le super-admin."
        
        # Protection des autres admins : Seul le super-admin peut les supprimer
        if user.role.nom == 'Admin':
            # Si celui qui supprime n'est pas le super-admin 'admin'
            if deleter.username != 'admin':
                return False, "Seul l'admin principal peut supprimer un autre admin."
            
        db.session.delete(user)
        db.session.commit()
        return True, "Utilisateur supprimé."
