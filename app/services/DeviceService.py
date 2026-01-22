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
        
    def create_player(self, nom, localisation, ip_address=None):
        try:
            # On en crée un nouveau directement
            new_lecteur = Lecteur(
                id_utilisateur=1, # Default admin user
                nom=nom,
                localisation=localisation,
                ip_address=ip_address,
                statut='ko',
                derniere_sync=datetime.utcnow(),
                historique=""
            )
            db.session.add(new_lecteur)
            db.session.commit()
            return new_lecteur
        except Exception as e:
            print(f"Error creating/updating player: {e}")
            db.session.rollback()
            return None
        
    def handle_heartbeat(self, player_id, data, client_ip=None):
        lecteur = Lecteur.query.get(player_id)
        if not lecteur:
            return None
            
        lecteur.derniere_sync = datetime.utcnow()
        lecteur.statut = 'ok'
        
        # Mise à jour IP si fournie et différente (ou nouvelle)
        if client_ip and lecteur.ip_address != client_ip:
            lecteur.ip_address = client_ip
        
        # Logique de réception d'état du client
        if data and data.get('is_audio_playing') is False:
             pass
             
        # RESET Au Démarrage : Si le client dit "je viens de démarrer", on efface son historique d'alertes
        if data and data.get('startup'):
            print(f" >> [DeviceService] Client {player_id} redémarré : RESET historique.")
            lecteur.historique = ""
            db.session.commit()
            return { "ok": True, "startup_ack": True }

        broadcast_msg = None
        # Cas 1 : URGENT (boucle infinie)
        # cas 1 : urgent (boucle infinie)
        if "URGENT:" in lecteur.historique:
             broadcast_msg = lecteur.historique.split("URGENT:")[1].strip()
             broadcast_msg = f"URGENT:{broadcast_msg}"
             
        # cas 2 : broadcast standard (one shot)
        elif "BROADCAST:" in lecteur.historique:
            broadcast_msg = lecteur.historique.split("BROADCAST:")[1].strip()
            # on marque le message comme lu/livre dans l'historique
            lecteur.historique = f"Dernière diffusion : {broadcast_msg} ({datetime.utcnow().strftime('%H:%M:%S')})"
            
        db.session.commit()

        return {
            "ok": True,
            "server_time": datetime.utcnow().isoformat(),
            "needs_sync_main": bool(broadcast_msg), 
            "needs_sync_fallback": False,
            "broadcast_command": broadcast_msg
        }

    def handle_auto_heartbeat(self, client_ip, data):
        """ Trouve le lecteur par IP et traite le heartbeat """
        if not client_ip:
            return None
            
        # Recherche par IP
        lecteur = Lecteur.query.filter_by(ip_address=client_ip).first()
        
        if not lecteur:
            # Optionnel : Auto-create "Inconnu" ?
            # Pour l'instant on retourne None => 403
            # ou on le log pour debug
            print(f" [AutoHeartbeat] IP inconnu : {client_ip}")
            return None
            
        print(f" [AutoHeartbeat] Lecteur identifié : {lecteur.nom} (ID: {lecteur.id_lecteur}) via IP {client_ip}")
        # On délègue au heartbeat standard, 
        # on renvoie aussi l'ID pour que le client puisse se configurer s'il est malin (optionnel)
        response = self.handle_heartbeat(lecteur.id_lecteur, data, client_ip)
        if response:
            response['player_id'] = lecteur.id_lecteur # On donne son ID au client
        return response
        
    def get_main_playlist_tracks(self, player_id):
        # 1. lire la configuration
        # (import local pour eviter les cycles)
        from app.services.DashboardService import DashboardService
        dash_service = DashboardService()
        config = dash_service.get_planning()
        
        # 2. si inactif (mode manuel pas encore active) => silence
        if not config.get('is_active'):
             return []
             
        # 3. logique horaire
        now = datetime.now()
        hour = now.hour
        target_media_id = None
        
        # 08h-12h : matin
        if 8 <= hour < 12:
            target_media_id = config.get('matin')
        # 12h-20h : apres-midi (ET NUIT pour éviter le silence à 00h)
        elif 12 <= hour or hour < 8:
             target_media_id = config.get('apres_midi')
        else:
             # nuit / hors plage : silence
             return []
             
        if not target_media_id:
             return []
             
        # 4. recuperer le media cible
        media = Media.query.get(target_media_id)
        if not media: 
            return []
            
        # 5. construire la reponse (playlist d'un seul titre en boucle)
        url = ""
        if hasattr(media, 'musiques') and media.musiques:
             url = media.musiques[0].url
        
        return [{
            'id': media.id_media,
            'title': media.nom,
            'file_url': url,
            'kind': media.type
        }]
