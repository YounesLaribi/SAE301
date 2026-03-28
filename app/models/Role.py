#Modele representant le role d'un utilisateur.
from app.extensions import db

class Role(db.Model):
    __tablename__ = 'Role'
    id_role = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    
    utilisateurs = db.relationship('Utilisateur', backref='role', lazy=True)
