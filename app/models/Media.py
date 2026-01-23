#modele representant un contenu (Musique, Pub, Urgence) dans la bibliotheque.
from app.extensions import db

class Media(db.Model):
    __tablename__ = 'Media'
    id_media = db.Column(db.Integer, primary_key=True, unique=True)
    id_playlist = db.Column(db.Integer, db.ForeignKey('Playlist.id_playlist'), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False, default='music')
    actif = db.Column(db.Boolean, nullable=False, default=True)
    prioritaire = db.Column(db.Boolean, nullable=False, default=False)
    
    plannings = db.relationship('Planning', backref='media', lazy=True)
    musiques = db.relationship('Musique', backref='media', lazy=True)
