from app import create_app, db
from app.models.Lecteur import Lecteur

app = create_app()
with app.app_context():
    try:
        lyon = Lecteur.query.filter(Lecteur.localisation.ilike('%Lyon%')).first()
        if not lyon:
            lyon = Lecteur.query.filter(Lecteur.nom.ilike('%Lyon%')).first()
            
        if lyon:
            print(f"Suppression de : {lyon.nom} (ID: {lyon.id_lecteur})")
            db.session.delete(lyon)
            db.session.commit()
            print("Succès.")
        else:
            print("Aucun lecteur 'Lyon' trouvé.")
    except Exception as e:
        print(f"Erreur: {e}")
