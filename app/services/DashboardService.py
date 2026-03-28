# Service gérant le tableau de bord, les statistiques et les actions administratives (Marketing, Sales, Urgence).
from app.models.Lecteur import Lecteur

from app.models.Media import Media
from app.models.Playlist import Playlist
from app.models.Musique import Musique
from app.extensions import db
from datetime import datetime, time

class DashboardService:
    def _update_player_statuses(self):
        TIMEOUT_SECONDS = 15
        lecteurs = Lecteur.query.all()
        now = datetime.utcnow()
        
        for l in lecteurs:
            if l.derniere_sync:
                delta = now - l.derniere_sync
                if delta.total_seconds() > TIMEOUT_SECONDS:
                    l.statut = 'ko'
                else:
                    l.statut = 'ok'
            else:
                l.statut = 'ko'
        
        db.session.commit()

    def get_admin_stats(self):
        self._update_player_statuses()
        return {
            'total': Lecteur.query.count(),
            'up': Lecteur.query.filter_by(statut='ok').count(),
            'ko': Lecteur.query.filter_by(statut='ko').count(),
            'critical': 0,
            'total_tracks': Media.query.count(),
            'players': Lecteur.query.all()
        }

    def get_monitoring_data(self):
        self._update_player_statuses()
        lecteurs = Lecteur.query.all()
        return {
             'players': lecteurs,
             'up': Lecteur.query.filter_by(statut='ok').count(),
             'ko': Lecteur.query.filter_by(statut='ko').count(),
             'critical': 0,
             'alerts': [],
             'total': len(lecteurs)
        }

    def get_marketing_data(self):
        return {
            'medias': Media.query.filter_by(type='music').all(),
            'playlists': Playlist.query.all(),
            'planning': self.get_planning()
        }

    def get_sales_data(self):
        return {
            'ads': Media.query.filter_by(type='ad').all()
        }
    
    def get_all_tracks(self):
        return Media.query.all()
    
    def get_summary_json(self):
        self._update_player_statuses()
        lecteurs = Lecteur.query.all()
        return {
            'players': [{
                'id': l.id_lecteur,
                'name': l.nom,
                'site': l.localisation,
                'status': l.statut,
                'last_seen_at': l.derniere_sync.isoformat() if l.derniere_sync else None
            } for l in lecteurs],
            'stats': {
                'up': Lecteur.query.filter_by(statut='ok').count(),
                'ko': Lecteur.query.filter_by(statut='ko').count()
            }
        }

    def add_track_to_library(self, title, url, kind):
        lecteur = Lecteur.query.first()
        
        if not lecteur:
            from app.models.Utilisateur import Utilisateur
            admin = Utilisateur.query.filter_by(username='admin').first()
            if admin:
                lecteur = Lecteur(
                    nom="SYSTEM_HQ", 
                    localisation="Server", 
                    statut="ok", 
                    derniere_sync=datetime.now(), 
                    historique="Init System", 
                    id_utilisateur=admin.id_utilisateur
                )
                db.session.add(lecteur)
                db.session.flush()
        
        if not lecteur:
            return None

        playlist = Playlist.query.filter_by(nom="Bibliothèque Globale").first()
        if not playlist:
            playlist = Playlist(nom="Bibliothèque Globale", version=1, id_lecteur=lecteur.id_lecteur)
            db.session.add(playlist)
            db.session.flush()
            
        new_media = Media(
            id_playlist=playlist.id_playlist,
            nom=title,
            type=kind.lower() if kind else 'music',
            actif=True
        )
        db.session.add(new_media)
        db.session.flush()
        
        default_duration = time(0, 3, 0) 
        
        new_musique = Musique(
            id_media=new_media.id_media,
            url=url,
            duree=default_duration
        )
        db.session.add(new_musique)
        
        db.session.commit()
        return new_media


    def get_track_by_id(self, track_id):
        return Media.query.get(track_id)

    def delete_track(self, track_id):
        media = Media.query.get(track_id)
        if media:
            Musique.query.filter_by(id_media=track_id).delete()
            db.session.delete(media)
            db.session.commit()
            return True
        return False

    def update_track(self, track_id, title, url, kind):
        media = Media.query.get(track_id)
        if media:
            media.nom = title
            media.type = kind.lower() if kind else 'music'
            
            musique = Musique.query.filter_by(id_media=track_id).first()
            if musique:
                musique.url = url
            
            db.session.commit()
            return True
        return False

    def get_urgent_data(self):
        return {
            'urgent_tracks': Media.query.filter_by(type='urgent').all()
        }

    def _send_to_all_history(self, text):
        lecteurs = Lecteur.query.all()
        for l in lecteurs:
            l.historique = text
        db.session.commit()
        return True

    def trigger_stop_music(self):
        return self._send_to_all_history("BROADCAST: STOP")

    def trigger_cancel_broadcast(self):
        return self._send_to_all_history("BROADCAST: CANCEL")

    def trigger_stop_urgent(self):
        return self.trigger_stop_music()

    def trigger_ad_broadcast(self, media_id):
        media = Media.query.get(media_id)
        if not media: return False
        
        url = "http://perdu.com"
        if media.musiques: url = media.musiques[0].url
        
        msg = f"BROADCAST:{media.nom}|{url}"
        return self._send_to_all_history(msg)

    def trigger_urgent_broadcast(self, media_id):
        media = Media.query.get(media_id)
        if not media: return False
        
        url = "http://perdu.com"
        if media.musiques: url = media.musiques[0].url
        
        msg = f"URGENT:{media.nom}|{url}"
        return self._send_to_all_history(msg)

    CONFIG_FILE = "scheduler_config.json"

    def _load_config(self):
        import os
        import json
        if not os.path.exists(self.CONFIG_FILE):
             return {"is_active": False, "matin": None, "apres_midi": None}
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"is_active": False, "matin": None, "apres_midi": None}

    def _save_config(self, config):
        import json
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def save_planning(self, matin_id, apres_midi_id):
        config = self._load_config()
        config['is_active'] = True
        config['matin'] = int(matin_id) if matin_id else None
        config['apres_midi'] = int(apres_midi_id) if apres_midi_id else None
        self._save_config(config)
        
        if config['is_active']:
            self.trigger_cancel_broadcast()

        return True

    def disable_planning(self):
        config = self._load_config()
        config['is_active'] = False
        self._save_config(config)
        return True

    def get_planning(self):
        return self._load_config()
