from app.extensions import db

class Lecteur(db.Model):
    __tablename__ = 'Lecteur'
    id_lecteur = db.Column(db.Integer, primary_key=True)
    id_utilisateur = db.Column(db.Integer, db.ForeignKey('Utilisateur.id_utilisateur'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    localisation = db.Column(db.String(200), nullable=False)
    statut = db.Column(db.String(10), nullable=False, default='ok') # 'ok' ou 'ko' (Monitoring)
    derniere_sync = db.Column(db.DateTime(timezone=True), nullable=False)
    historique = db.Column(db.String(255), nullable=False)
    
    # Relation : Un lecteur possède une playlist active
    playlists = db.relationship('Playlist', backref='lecteur', lazy=True)
