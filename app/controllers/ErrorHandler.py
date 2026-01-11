from flask import Blueprint

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return "Page non trouvée", 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return "Erreur interne du serveur", 500
