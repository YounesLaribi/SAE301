from flask import Blueprint, request, jsonify, redirect, url_for, flash, abort, render_template
from flask_login import login_required, current_user
from app.services.DeviceService import DeviceService

"""
    ce module gère les routes et les fonctionnalités liées aux terminaux (lecteurs).
    Il inclut les routes pour les terminaux et les routes API pour les terminaux.
"""

#instance du service
device_service = DeviceService()
from functools import wraps

devices_bp = Blueprint('devices', __name__)
# point de terminaison api correspondant àl'original api.py
api_bp = Blueprint('api', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.role or current_user.role.nom != 'Admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- routes admin (interface utilisateur) ---

#détail d'un terminal spécifique
@devices_bp.route('/players/<int:lecteur_id>')
@login_required
def player_detail(lecteur_id):
    lecteur = device_service.get_player_or_404(lecteur_id)
    alerts = [] # simulation d'alerte vides pour la démo
    return render_template('player_detail.html', player=lecteur, alerts=alerts)

# suppression d'un lecteur (action sensible)
@devices_bp.route('/players/delete/<int:lecteur_id>', methods=['POST'])
@login_required
@admin_required # protection maximale : seul l'admin peut supprimer
def delete_lecteur(lecteur_id):
    if device_service.delete_player(lecteur_id):
        pass #supprimé avec succès
    else:
        abort(404) #ou flasher une erreur
    flash('Lecteur supprimé.')
    return redirect(url_for('admin.dashboard'))


# --- Routes API (proviennent de api.py) ---




@api_bp.route('/players/<int:player_id>/heartbeat', methods=['POST'])
def heartbeat(player_id):
    data = request.json
    # On passe l'IP du client pour mise à jour dynamique
    client_ip = request.remote_addr
    response_data = device_service.handle_heartbeat(player_id, data, client_ip)
    
    if not response_data:
         return jsonify({'error': 'Unauthorized or Not Found'}), 401
         
    return jsonify(response_data)

@api_bp.route('/heartbeat/auto', methods=['POST'])
def auto_heartbeat():
    """
    Endpoint générique qui identifie le lecteur par son adresse IP source.
    """
    data = request.json
    client_ip = request.remote_addr
    
    # On demande au service de trouver ou gérer ce client par IP
    response_data = device_service.handle_auto_heartbeat(client_ip, data)
    
    if not response_data:
        # Si IP inconnue et qu'on ne veut pas auto-créer, on rejette
        return jsonify({'error': 'Unknown client IP. Please register in Dashboard.'}), 403
        
    return jsonify(response_data)

@api_bp.route('/players/<int:player_id>/playlists/main', methods=['GET'])
def get_main_playlist(player_id):
    tracks = device_service.get_main_playlist_tracks(player_id)
    if tracks is None:
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify(tracks)

@api_bp.route('/players/<int:player_id>/playlists/fallback', methods=['GET'])
def get_fallback_playlist(player_id):
    #liste vide par défaut pour le repli (fallback)
    return jsonify([])

@api_bp.route('/players/<int:player_id>/commands', methods=['GET'])
def get_commands(player_id):
    return jsonify([])

@api_bp.route('/players/<int:player_id>/commands/ack', methods=['POST'])
def ack_command(player_id):
    return jsonify({'ok': True})
