from app.models.Playlist import Playlist
from app.models.PlaylistDAOInterface import PlaylistDAOInterface
from app.extensions import db

class PlaylistDAO(PlaylistDAOInterface):
    def create(self, playlist):
        db.session.add(playlist)
        db.session.commit()
        return playlist

    def get_by_id(self, id_playlist):
        return Playlist.query.get(id_playlist)

    def get_all(self):
        return Playlist.query.all()

    def update(self, playlist):
        db.session.commit()
        return playlist

    def delete(self, id_playlist):
        playlist = self.get_by_id(id_playlist)
        if playlist:
            db.session.delete(playlist)
            db.session.commit()
