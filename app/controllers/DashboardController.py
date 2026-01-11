from flask import Blueprint, render_template, redirect, url_for, abort, jsonify, request, flash
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
# Note architecturale : Initialement prévu dans DevicesController, mais la gestion des médias
# est plus logique ici dans le contexte du tableau de bord d'administration.
# Une refactorisation future pourrait créer un MediaController dédié si la complexité augmente.
@admin_bp.route('/media')
@login_required
def tracks():
    medias = dashboard_service.get_all_tracks()
    return render_template('tracks.html', tracks=medias)

@admin_bp.route('/media/add', methods=['POST'])
@login_required
def add_track():
    title = request.form.get('title')
    url = request.form.get('url')
    kind = request.form.get('kind')
    
    if title and url:
        dashboard_service.add_track_to_library(title, url, kind)
        flash('Titre ajouté avec succès.', 'success')
    else:
        flash('Erreur: Titre et URL requis.', 'danger')
        
    return redirect(url_for('admin.tracks'))

@admin_bp.route('/media/delete/<int:track_id>', methods=['POST'])
@login_required
def delete_track(track_id):
    if current_user.role.nom != 'Admin':
        abort(403)
        
    if dashboard_service.delete_track(track_id):
        flash('Titre supprimé.', 'success')
    else:
        flash('Erreur lors de la suppression.', 'danger')
        
    return redirect(url_for('admin.tracks'))

@admin_bp.route('/media/edit/<int:track_id>', methods=['GET', 'POST'])
@login_required
def edit_track(track_id):
    if current_user.role.nom != 'Admin':
        abort(403)
        
    track = dashboard_service.get_track_by_id(track_id)
    if not track:
        abort(404)
        
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        kind = request.form.get('kind')
        
        if dashboard_service.update_track(track_id, title, url, kind):
            flash('Titre mis à jour.', 'success')
            return redirect(url_for('admin.tracks'))
        else:
            flash('Erreur lors de la modification.', 'danger')
            
    return render_template('track_edit.html', track=track)

@admin_bp.route('/urgent')
@login_required
def urgent_dashboard():
    data = dashboard_service.get_urgent_data()
    return render_template('urgent.html', **data)

# Route de redirection pour les tests de santé
@admin_bp.route('/check-health')
@login_required
def check_health():
    return redirect(url_for('admin.dashboard'))
