from app.extensions import db
from flask_login import UserMixin
import bcrypt

class Utilisateur(UserMixin, db.Model):
    __tablename__ = 'Utilisateur'
    id_utilisateur = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime(timezone=True))
    id_role = db.Column(db.Integer, db.ForeignKey('Role.id_role'), nullable=False)
    
    lecteurs = db.relationship('Lecteur', backref='utilisateur', lazy=True)

    def get_id(self):
        return str(self.id_utilisateur)

    def set_password(self, password):
        password_bytes = password.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        self.password = hashed_bytes.decode('utf-8')

    def check_password(self, password):
        password_bytes = password.encode('utf-8')
        hashed_bytes = self.password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
