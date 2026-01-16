from app.models.Lecteur import Lecteur
from app.models.Alerte import Alerte
from app.models.Media import Media
from app.models.Playlist import Playlist
from app.models.Musique import Musique
from app.extensions import db
from datetime import datetime, time

class DashboardService:
    def _update_player_statuses(self):
        # Timeout de 15 secondes pour considérer un lecteur comme déconnecté
        TIMEOUT_SECONDS = 15
        lecteurs = Lecteur.query.all()
        now = datetime.utcnow()
        
        for l in lecteurs:
            if l.derniere_sync:
                # Calcul basique, on suppose que les dates sont en UTC ou naïves cochées
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
            'critical': Alerte.query.count(),
            'total_tracks': Media.query.filter_by(type='music').count(),
            'players': Lecteur.query.all()
        }

    def get_monitoring_data(self):
        self._update_player_statuses()
        lecteurs = Lecteur.query.all()
        return {
             'players': lecteurs,
             'up': Lecteur.query.filter_by(statut='ok').count(),
             'ko': Lecteur.query.filter_by(statut='ko').count(),
             'critical': Alerte.query.count(),
             'alerts': Alerte.query.all(),
             'total': len(lecteurs)
        }

    def get_marketing_data(self):
        return {
            'medias': Media.query.filter_by(type='music').all(),
            'playlists': Playlist.query.all()
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
        # 0. Récupérer un lecteur pour attacher la playlist (Constraint FK)
        lecteur = Lecteur.query.first()
        
        if not lecteur:
            # Création d'un lecteur système par défaut si aucun n'existe
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
            # Si toujours pas de lecteur (pas d'admin?), on ne peut pas créer la playlist
            return None

        # 1. Gestion de la Playlist par défaut
        # On cherche une playlist "Bibliothèque Globale" associée à ce lecteur
        playlist = Playlist.query.filter_by(nom="Bibliothèque Globale").first()
        if not playlist:
            playlist = Playlist(nom="Bibliothèque Globale", version=1, id_lecteur=lecteur.id_lecteur)
            db.session.add(playlist)
            db.session.flush() # Pour récupérer l'ID
            
        # 2. Création du Média
        new_media = Media(
            id_playlist=playlist.id_playlist,
            nom=title,
            type=kind.lower() if kind else 'music',
            actif=True
        )
        db.session.add(new_media)
        db.session.flush()
        
        # 3. Création du fichier Musique associé
        # Durée par défaut temporaire (3 mins) car on ne peut pas analyser le fichier pour l'instant
        default_duration = time(0, 3, 0) 
        
        new_musique = Musique(
            id_media=new_media.id_media,
            url=url,
            duree=default_duration
        )
        db.session.add(new_musique)
        
        # 4. Commit final
        db.session.commit()
        return new_media


    def get_track_by_id(self, track_id):
        return Media.query.get(track_id)

    def delete_track(self, track_id):
        media = Media.query.get(track_id)
        if media:
            # Supprimer les musiques associées d'abord (Cascade manuelle si pas définie en DB)
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
            
            # Mise à jour de l'URL (table Musique)
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

    def trigger_broadcast(self, message):
        """
        Déclenche une diffusion prioritaire sur tous les lecteurs.
        Utilise le champ 'historique' comme canal de commande temporaire.
        """
        lecteurs = Lecteur.query.all()
        for l in lecteurs:
            l.historique = f"BROADCAST: {message}"
        db.session.commit()
        return True

    def trigger_stop_music(self):
        """
        Envoie un ordre d'arrêt immédiat à tous les lecteurs (MUTE).
        Utilisé par Marketing et Stop Général.
        """
        return self.trigger_broadcast("STOP")

    def trigger_cancel_broadcast(self):
        """
        Annule la diffusion en cours (Sales) et reprend la musique normale.
        """
        return self.trigger_broadcast("CANCEL")

    def trigger_stop_urgent(self):
        """
        Arrête l'urgence en cours et reprend la musique normale.
        """
        lecteurs = Lecteur.query.all()
        for l in lecteurs:
            # On nettoie l'historique s'il contient URGENT
            if "URGENT:" in l.historique:
                l.historique = "BROADCAST: CANCEL"
            else:
                l.historique = "BROADCAST: CANCEL"
        db.session.commit()
        return True

    def trigger_urgent_broadcast(self, media_id):
        """
        Déclenche une diffusion URGENTE (boucle) sur tous les lecteurs.
        """
        media = Media.query.get(media_id)
        if not media:
            return False
            
        message = f"URGENT:{media.nom}"
        lecteurs = Lecteur.query.all()
        for l in lecteurs:
            l.historique = message
        db.session.commit()
        return True
