from app.extensions import db

class Musique(db.Model):
    __tablename__ = 'Musique'
    id_musique = db.Column(db.Integer, primary_key=True)
    id_media = db.Column(db.Integer, db.ForeignKey('Media.id_media'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    duree = db.Column(db.Time, nullable=False)
