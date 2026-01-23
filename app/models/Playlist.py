from app.extensions import db
from datetime import datetime

class Playlist(db.Model):
    __tablename__ = 'Playlist'
    id_playlist = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    version = db.Column(db.String(20), nullable=False, default='1')
    date_mise_a_jour = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    id_lecteur = db.Column(db.Integer, db.ForeignKey('Lecteur.id_lecteur'), nullable=False)
    
    medias = db.relationship('Media', backref='playlist', lazy=True)
