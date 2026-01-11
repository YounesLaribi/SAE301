from app.extensions import db

class Alerte(db.Model):
    __tablename__ = 'Alerte'
    id_alerte = db.Column(db.Integer, primary_key=True)
    id_media = db.Column(db.Integer, db.ForeignKey('Media.id_media'), nullable=False)
    type = db.Column(db.String(255), nullable=False) # Ex: 'NO_AUDIO', 'NETWORK_ERROR'
    message = db.Column(db.String(255), nullable=False)
