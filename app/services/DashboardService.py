from app.models.Lecteur import Lecteur
from app.models.Alerte import Alerte
from app.models.Media import Media
from app.models.Playlist import Playlist

class DashboardService:
    def get_admin_stats(self):
        return {
            'total': Lecteur.query.count(),
            'up': Lecteur.query.filter_by(statut='ok').count(),
            'ko': Lecteur.query.filter_by(statut='ko').count(),
            'critical': Alerte.query.count(),
            'total_tracks': Media.query.filter_by(type='music').count(),
            'players': Lecteur.query.all()
        }

    def get_monitoring_data(self):
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
