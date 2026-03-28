# Modele representant la planification de diffusion (Matin, Apres-midi).
from app.extensions import db

class Planning(db.Model):
    __tablename__ = 'Planning'
    date_heure = db.Column(db.DateTime(timezone=True), primary_key=True)
    id_media = db.Column(db.Integer, db.ForeignKey('Media.id_media'), primary_key=True)
