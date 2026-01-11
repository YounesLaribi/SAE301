from flask import Blueprint, render_template, redirect, url_for, abort, jsonify
from flask_login import login_required, current_user
from app.services.DashboardService import DashboardService

# Initialisation du service
dashboard_service = DashboardService()

# On garde le nom 'admin' pour le blueprint afin que les redirections 'admin.dashboard' existantes fonctionnent.
# Si on voulait suivre le nom du fichier strictement, on mettrait 'dashboard', mais limitons les cassures.
admin_bp = Blueprint('admin', __name__)

# Route principale du dashboard
@admin_bp.route('/')
@login_required # Sécurité : il faut être connecté
def dashboard():
    """
    Point d'entrée principal après la connexion. 
    Redirige les utilisateurs vers leur tableau de bord spécifique selon leur rôle.
    """
    if not current_user.role:
        return "Erreur: Rôle non défini pour cet utilisateur.", 403
        
    role = current_user.role.nom
    # Logique de redirection basée sur le rôle (RBAC)
    if role == 'Marketing':
        return redirect(url_for('admin.marketing_dashboard'))
    elif role == 'Sales':
        return redirect(url_for('admin.sales_dashboard'))
        
    # Si c'est un Admin, on prépare les statistiques globales pour la vue d'ensemble
    stats = dashboard_service.get_admin_stats()
    
    # Rendu de la page d'accueil Admin avec les données calculées
    return render_template('dashboard.html', **stats)

# Vue technique (Monitoring IT)
@admin_bp.route('/it')
@login_required
def monitoring_it():
    """
    Affiche l'état technique détaillé des terminaux Raspberry Pi.
    Cette vue est réservée à la maintenance et à la surveillance réseau.
    """
    data = dashboard_service.get_monitoring_data()
    return render_template('admin_dashboard.html', **data)

# Vue Marketing
@admin_bp.route('/marketing')
@login_required
def marketing_dashboard():
    """
    Interface dédiée à la gestion de l'ambiance sonore et des playlists.
    Sécurité : Seul le Marketing et l'Admin peuvent accéder ici.
    """
    if current_user.role.nom not in ['Admin', 'Marketing']:
        abort(403)
    data = dashboard_service.get_marketing_data()
    return render_template('marketing.html', **data)

# Vue Sales (Commercial)
@admin_bp.route('/sales')
@login_required
def sales_dashboard():
    """
    Interface pour la diffusion de publicités et de messages prioritaires.
    Sécurité : Seul le département Sales et l'Admin y ont accès.
    """
    if current_user.role.nom not in ['Admin', 'Sales']:
        abort(403)
    data = dashboard_service.get_sales_data()
    return render_template('sales.html', **data)

# Endpoint API Interne pour récupérer les statistiques en JSON
# Conservé dans Dashboard car utilisé par le tableau de bord
@admin_bp.route('/api/admin/summary')
@login_required
def summary():
    """
    Renvoie les données de monitoring au format JSON pour des mises à jour dynamiques.
    """
    return jsonify(dashboard_service.get_summary_json())

# Gestion de la bibliothèque de titres
# Déplacer les pistes ici ou dans MediaController ? 
# Le plan prévoyait DevicesController pour les lecteurs... vérifions Media/Tracks.
# Pas de MediaController dans l'architecture actuelle. Dashboard convient ou peut-être un nouveau MediaController ?
# L'image montre uniquement : Dashboard, Devices, ErrorHandler, Log, Login, Organisation, Timetable, User.
# Les pistes s'intègrent mieux dans Dashboard ou peut-être Organisation ? Gardons Dashboard pour l'instant car cela faisait partie de la logique admin.
@admin_bp.route('/media')
@login_required
def tracks():
    medias = dashboard_service.get_all_tracks()
    return render_template('tracks.html', tracks=medias)

@admin_bp.route('/media/add', methods=['POST'])
@login_required
def add_track():
    # Logique d'upload à implémenter ici
    return redirect(url_for('admin.tracks'))

# Route de redirection pour les tests de santé
@admin_bp.route('/check-health')
@login_required
def check_health():
    return redirect(url_for('admin.dashboard'))
