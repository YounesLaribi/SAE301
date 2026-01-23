# Utilitaires pour initialiser la base de donnees (Roles et Utilisateurs uniquement).
from datetime import datetime
from app.extensions import db
from app.models import Role, Utilisateur, Lecteur, Playlist, Media, Musique

def seed_db():
    db.create_all()

    if Role.query.first():
        return

    print("Initialisation de la base de données (Roles & Utilisateurs)...")

    role_admin = Role(nom="Admin")
    role_marketing = Role(nom="Marketing")
    role_sales = Role(nom="Sales")
    
    db.session.add_all([role_admin, role_marketing, role_sales])
    db.session.commit()

    def create_user(username, password, role):
        if not Utilisateur.query.filter_by(username=username).first():
            user = Utilisateur(username=username, id_role=role.id_role)
            user.set_password(password)
            db.session.add(user)

    create_user("admin", "admin", role_admin)
    create_user("marketing", "marketing", role_marketing)
    create_user("sales", "sales", role_sales)
    
    db.session.commit()
    print("Base de données initialisée (Admin/Marketing/Sales créés).")
