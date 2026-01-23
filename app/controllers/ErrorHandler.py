from flask import Blueprint

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def erreur_non_trouve(error):
    return "Page non trouvée", 404

@errors_bp.app_errorhandler(500)
def erreur_interne(error):
    return "Erreur interne du serveur", 500
