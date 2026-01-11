from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager

# Fabrique d'application (Application Factory Pattern)
# Ce pattern permet de créer plusieurs instances de l'application si nécessaire (ex: tests).
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class) # Chargement de la configuration (Clés secrètes, DB)

    # Initialisation des extensions Flask (Base de données et Sessions)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Contexte de l'application pour les opérations initiales
    with app.app_context():
        from app import models # Enregistrement des modèles SQL
        from app.utils import seed_db 
        seed_db() # Lancement du script d'initialisation (Fausse données)

    # ENREGISTREMENT DES BLUEPRINTS (Modularité)
    from app.controllers.DevicesController import api_bp, devices_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(devices_bp)

    from app.controllers.DashboardController import admin_bp
    app.register_blueprint(admin_bp)

    from app.controllers.LoginController import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.controllers.UserController import user_bp
    app.register_blueprint(user_bp)

    from app.controllers.ErrorHandler import errors_bp
    app.register_blueprint(errors_bp)
    
    # Placeholders (Optional registration if empty)
    # from app.controllers.LogController import log_bp
    # app.register_blueprint(log_bp)
    # from app.controllers.OrganisationController import organisation_bp
    # app.register_blueprint(organisation_bp)
    # from app.controllers.TimetableController import timetable_bp
    # app.register_blueprint(timetable_bp)

    # Affichage des routes au démarrage (pour le débogage)
    print("All routes registered:")
    # for rule in app.url_map.iter_rules():
    #     print(f" - {rule}")

    return app
