# Service gérant les terminaux (lecteurs), leur état (heartbeat) et la récupération des playlists.
from app.models.Lecteur import Lecteur
from app.models.Playlist import Playlist
from app.models.Media import Media
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
        
        if data and data.get('is_audio_playing') is False:
             pass
             
        if data and data.get('startup'):
            print(f" >> [DeviceService] Client {player_id} redémarré : RESET historique.")
            lecteur.historique = ""
            db.session.commit()
            return { "ok": True, "startup_ack": True }

        broadcast_msg = None
        if "URGENT:" in lecteur.historique:
             broadcast_msg = lecteur.historique.split("URGENT:")[1].strip()
             broadcast_msg = f"URGENT:{broadcast_msg}"
             
        elif "BROADCAST:" in lecteur.historique:
            broadcast_msg = lecteur.historique.split("BROADCAST:")[1].strip()
            lecteur.historique = f"Dernière diffusion : {broadcast_msg} ({datetime.utcnow().strftime('%H:%M:%S')})"
            
        db.session.commit()

        return {
            "ok": True,
            "server_time": datetime.utcnow().isoformat(),
            "needs_sync_main": bool(broadcast_msg), 
            "needs_sync_fallback": False,
            "broadcast_command": broadcast_msg
        }
        
    def get_main_playlist_tracks(self, player_id):
        from app.services.DashboardService import DashboardService
        dash_service = DashboardService()
        config = dash_service.get_planning()
        
        if not config.get('is_active'):
             return []
             
        now = datetime.now()
        hour = now.hour
        target_media_id = None
        
        if 8 <= hour < 12:
            target_media_id = config.get('matin')
        elif 12 <= hour < 24:
             target_media_id = config.get('apres_midi')
        else:
             return []
             
        if not target_media_id:
             return []
             
        media = Media.query.get(target_media_id)
        if not media: 
            return []
            
        url = ""
        if hasattr(media, 'musiques') and media.musiques:
             url = media.musiques[0].url
        
        return [{
            'id': media.id_media,
            'title': media.nom,
            'file_url': url,
            'kind': media.type
        }]
