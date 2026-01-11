from flask import Blueprint, request, jsonify, redirect, url_for, flash, abort, render_template
from flask_login import login_required, current_user
from app.services.DeviceService import DeviceService

# Instance du service
device_service = DeviceService()
from functools import wraps

devices_bp = Blueprint('devices', __name__)
# Point de terminaison API correspondant à l'original api.py
api_bp = Blueprint('api', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.role or current_user.role.nom != 'Admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- Routes Admin (Interface Utilisateur) ---

# Détail d'un terminal spécifique
@devices_bp.route('/players/<int:lecteur_id>')
@login_required
def player_detail(lecteur_id):
    lecteur = device_service.get_player_or_404(lecteur_id)
    alerts = [] # Simulation d'alertes vides pour la démo
    return render_template('player_detail.html', player=lecteur, alerts=alerts)

# Suppression d'un lecteur (Action sensible)
@devices_bp.route('/players/delete/<int:lecteur_id>', methods=['POST'])
@login_required
@admin_required # Protection maximale : seul l'admin peut supprimer
def delete_lecteur(lecteur_id):
    if device_service.delete_player(lecteur_id):
        pass # Supprimé avec succès
    else:
        abort(404) # Ou flasher une erreur
    flash('Lecteur supprimé.')
    return redirect(url_for('admin.dashboard'))


# --- Routes API (Proviennent de api.py) ---




@api_bp.route('/players/<int:player_id>/heartbeat', methods=['POST'])
def heartbeat(player_id):
    data = request.json
    response_data = device_service.handle_heartbeat(player_id, data)
    
    if not response_data:
         return jsonify({'error': 'Unauthorized or Not Found'}), 401
         
    return jsonify(response_data)

@api_bp.route('/players/<int:player_id>/playlists/main', methods=['GET'])
def get_main_playlist(player_id):
    tracks = device_service.get_main_playlist_tracks(player_id)
    if tracks is None:
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify(tracks)

@api_bp.route('/players/<int:player_id>/playlists/fallback', methods=['GET'])
def get_fallback_playlist(player_id):
    # Liste vide par défaut pour le repli (fallback)
    return jsonify([])

@api_bp.route('/players/<int:player_id>/commands', methods=['GET'])
def get_commands(player_id):
    return jsonify([])

@api_bp.route('/players/<int:player_id>/commands/ack', methods=['POST'])
def ack_command(player_id):
    return jsonify({'ok': True})
