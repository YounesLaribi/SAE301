from app.models.Media import Media
from app.models.MediaDAOInterface import MediaDAOInterface
from app.extensions import db

class MediaDAO(MediaDAOInterface):
    def create(self, media):
        db.session.add(media)
        db.session.commit()
        return media

    def get_by_id(self, id_media):
        return Media.query.get(id_media)

    def get_all(self):
        return Media.query.all()

    def update(self, media):
        db.session.commit()
        return media

    def delete(self, id_media):
        media = self.get_by_id(id_media)
        if media:
            db.session.delete(media)
            db.session.commit()
