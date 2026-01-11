from app.models.Lecteur import Lecteur
from app.models.Playlist import Playlist
from app.extensions import db
from datetime import datetime

class DeviceService:
    def get_player(self, player_id):
        return Lecteur.query.get(player_id)
    
    def get_player_or_404(self, player_id):
        return Lecteur.query.get_or_404(player_id)

    def delete_player(self, player_id):
        lecteur = Lecteur.query.get(player_id)
        if lecteur:
            db.session.delete(lecteur)
            db.session.commit()
            return True
        return False
        
    def handle_heartbeat(self, player_id, data):
        lecteur = Lecteur.query.get(player_id)
        if not lecteur:
            return None
            
        lecteur.derniere_sync = datetime.utcnow()
        lecteur.statut = 'ok'
        # les données peuvent être None si request.json est None, à manipuler avec précaution si nécessaire
        # Mais le contrôleur passe request.json. 
        if data and data.get('is_audio_playing') is False:
             # La logique pour l'alerte pourrait aller ici
             pass
        db.session.commit()
        
        return {
            "ok": True,
            "server_time": datetime.utcnow().isoformat(),
            "needs_sync_main": False,
            "needs_sync_fallback": False
        }
        
    def get_main_playlist_tracks(self, player_id):
        lecteur = Lecteur.query.get(player_id)
        if not lecteur:
             return None
             
        playlists = Playlist.query.filter_by(id_lecteur=lecteur.id_lecteur).all()
        tracks = []
        if playlists:
            pl = playlists[0]
            for m in pl.medias:
                url = ""
                # En supposant que Media possède une relation 'musiques'
                if hasattr(m, 'musiques') and m.musiques:
                     url = m.musiques[0].url
                
                tracks.append({
                    'id': m.id_media,
                    'title': m.nom,
                    'file_url': url,
                    'kind': m.type
                })
        return tracks
