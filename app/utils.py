from datetime import datetime
from app.extensions import db
from app.models import Role, Utilisateur, Lecteur, Playlist, Media, Musique

def seed_db():
    db.create_all()

    if Role.query.first():
        return

    print("Initialisation de la base de données avec les données par défaut...")

    role_admin = Role(nom="Admin")
    role_marketing = Role(nom="Marketing")
    role_sales = Role(nom="Sales")
    
    db.session.add_all([role_admin, role_marketing, role_sales])
    db.session.commit()

    def create_user(username, password, role):
        if not Utilisateur.query.filter_by(username=username).first():
            user = Utilisateur(username=username, id_role=role.id_role)
            user.set_password(password)
            db.session.add(user)

    create_user("admin", "admin", role_admin)
    create_user("marketing", "marketing", role_marketing)
    create_user("sales", "sales", role_sales)
    
    client_user = Utilisateur.query.filter_by(username="marketing").first()
    
    db.session.commit()

    lecteur1 = Lecteur(
        id_utilisateur=client_user.id_utilisateur,
        nom="Lecteur Paris",
        localisation="Paris HQ",
        statut="ok",
        derniere_sync=datetime.utcnow(),
        historique="Chanson actuelle"
    )
    lecteur2 = Lecteur(
        id_utilisateur=client_user.id_utilisateur,
        nom="Lecteur Lyon",
        localisation="Lyon Branch",
        statut="ko",
        derniere_sync=datetime.utcnow(),
        historique="Silence"
    )
    db.session.add_all([lecteur1, lecteur2])
    db.session.commit()

    pl1 = Playlist(nom="Playlist Eté", version="1.0", id_lecteur=lecteur1.id_lecteur)
    db.session.add(pl1)
    db.session.commit()

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
