from app.models.Role import Role
from app.models.Utilisateur import Utilisateur
from app.models.Lecteur import Lecteur
from app.models.Playlist import Playlist
from app.models.Media import Media
from app.models.Planning import Planning

from app.models.Musique import Musique
from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return Utilisateur.query.get(int(user_id))
