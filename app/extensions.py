# Initialisation des extensions Flask (SQLAlchemy, Migrate, LoginManager) partagees dans l'application.
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
