from datetime import datetime
from app.extensions import db
from app.models import Role, Utilisateur, Lecteur, Playlist, Media, Musique

# Script utilitaire pour préparer l'environnement de démo
def seed_db():
    """
    Initialise la base de données avec des comptes et des données de test.
    C'est ce qui garantit que l'app est 'prête à l'emploi' dès le premier lancement.
    """
    # Création automatique des tables si elles n'existent pas
    db.create_all()

    # Si les rôles existent déjà, on ne fait rien
    if Role.query.first():
        return

    print("Initialisation de la base de données avec les données par défaut...")

    # 1. Création des Rôles métiers (Architecture RBAC)
    role_admin = Role(nom="Admin")
    role_marketing = Role(nom="Marketing")
    role_sales = Role(nom="Sales")
    
    db.session.add_all([role_admin, role_marketing, role_sales])
    db.session.commit()

    # 2. Création des Utilisateurs de démonstration
    # Chaque utilisateur se voit attribuer un rôle spécifique.
    def create_user(username, password, role):
        if not Utilisateur.query.filter_by(username=username).first():
            user = Utilisateur(username=username, id_role=role.id_role)
            user.set_password(password) # Sécurisation automatique (Hachage)
            db.session.add(user)

    create_user("admin", "admin", role_admin)
    create_user("marketing", "marketing", role_marketing)
    create_user("sales", "sales", role_sales)
    
    # Récupération du compte marketing pour lier les terminaux de test
    client_user = Utilisateur.query.filter_by(username="marketing").first()
    
    db.session.commit()

    # 3. Création de terminaux Raspberry Pi fictifs (Monitoring)
    lecteur1 = Lecteur(
        id_utilisateur=client_user.id_utilisateur,
        nom="Lecteur Paris",
        localisation="Paris HQ",
        statut="ok", # Simulé en ligne
        derniere_sync=datetime.utcnow(),
        historique="Chanson actuelle"
    )
    lecteur2 = Lecteur(
        id_utilisateur=client_user.id_utilisateur,
        nom="Lecteur Lyon",
        localisation="Lyon Branch",
        statut="ko", # Simulé hors-ligne pour la démo technique
        derniere_sync=datetime.utcnow(),
        historique="Silence"
    )
    db.session.add_all([lecteur1, lecteur2])
    db.session.commit()

    # 4. Création de playlists et de médias (Ambiances et Pubs)
    pl1 = Playlist(nom="Playlist Eté", version="1.0", id_lecteur=lecteur1.id_lecteur)
    db.session.add(pl1)
    db.session.commit()

    # Ajout d'une musique standard (Marketing)
    m1 = Media(id_playlist=pl1.id_playlist, nom="Song A", type="music")
    db.session.add(m1)
    db.session.commit()

    mus1 = Musique(
        id_media=m1.id_media, 
        url="http://music.com/a.mp3", 
        duree=datetime.strptime("00:03:00", "%H:%M:%S").time()
    )
    db.session.add(mus1)
    db.session.commit()

    # Ajout d'une publicité prioritaire (Sales)
    m2 = Media(id_playlist=pl1.id_playlist, nom="Flash Promo -10%", type="ad", prioritaire=True)
    db.session.add(m2)
    db.session.commit()

    mus2 = Musique(
        id_media=m2.id_media, 
        url="http://ads.com/promo.mp3", 
        duree=datetime.strptime("00:00:30", "%H:%M:%S").time()
    )
    db.session.add(mus2)
    db.session.commit()

    print("Base de données initialisée avec succès !")
