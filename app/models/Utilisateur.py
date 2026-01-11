from app.extensions import db
from flask_login import UserMixin
import bcrypt

class Utilisateur(UserMixin, db.Model):
    __tablename__ = 'Utilisateur'
    id_utilisateur = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False) # Empreinte du mot de passe (Crypté avec Bcrypt)
    last_login = db.Column(db.DateTime(timezone=True))
    id_role = db.Column(db.Integer, db.ForeignKey('Role.id_role'), nullable=False)
    
    # Relation : Un gestionnaire peut posséder plusieurs lecteurs audio
    lecteurs = db.relationship('Lecteur', backref='utilisateur', lazy=True)

    # Identifiant utilisé par Flask-Login
    def get_id(self):
        return str(self.id_utilisateur)

    # ALGORITHME DE SÉCURITÉ : Hachage du mot de passe avec Bcrypt
    def set_password(self, password):
        password_bytes = password.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        self.password = hashed_bytes.decode('utf-8')

    # Vérification cryptographique du mot de passe fourni
    def check_password(self, password):
        password_bytes = password.encode('utf-8')
        hashed_bytes = self.password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
