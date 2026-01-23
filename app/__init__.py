# Fichier d'initialisation de l'application Flask. Configure les extensions et enregistre les blueprints.
from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    with app.app_context():
        from app import models
        from app.utils import seed_db 
        seed_db()

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

    return app
